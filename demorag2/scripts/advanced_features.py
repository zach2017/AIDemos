#!/usr/bin/env python3
"""
Iceberg Advanced Features Demo - Time Travel & Schema Evolution
"""

import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from datetime import datetime

S3_ENDPOINT = "http://localstack:4566"
S3_BUCKET = "iceberg-warehouse"


def create_spark_session():
    """Create Spark session with Iceberg configuration"""
    spark = SparkSession.builder \
        .appName("IcebergAdvancedDemo") \
        .config("spark.jars.packages", 
                "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3,"
                "org.apache.hadoop:hadoop-aws:3.3.4,"
                "software.amazon.awssdk:bundle:2.20.18") \
        .config("spark.sql.extensions", 
                "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.demo", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.demo.type", "hadoop") \
        .config("spark.sql.catalog.demo.warehouse", f"s3a://{S3_BUCKET}/warehouse") \
        .config("spark.hadoop.fs.s3a.endpoint", S3_ENDPOINT) \
        .config("spark.hadoop.fs.s3a.access.key", "test") \
        .config("spark.hadoop.fs.s3a.secret.key", "test") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    return spark


def demo_time_travel(spark):
    """Demonstrate Iceberg time travel capabilities"""
    print("\n" + "="*70)
    print(" Demo 1: Time Travel with Iceberg")
    print("="*70)
    
    # Create a new table for time travel demo
    table_name = "demo.products_db.products_history"
    
    print(f"\n📝 Creating table: {table_name}")
    spark.sql(f"DROP TABLE IF EXISTS {table_name}")
    
    # Version 1: Initial data
    data_v1 = [
        (1, "Laptop", 1000.0, 10),
        (2, "Mouse", 25.0, 50),
        (3, "Keyboard", 75.0, 30)
    ]
    df_v1 = spark.createDataFrame(data_v1, ["id", "name", "price", "quantity"])
    df_v1.writeTo(table_name).using("iceberg").create()
    
    print("\n✅ Version 1: Initial load")
    spark.sql(f"SELECT * FROM {table_name}").show()
    
    # Get snapshot ID for version 1
    snapshots_v1 = spark.sql(f"SELECT snapshot_id FROM {table_name}.snapshots").collect()
    snapshot_v1 = snapshots_v1[0].snapshot_id
    print(f"   Snapshot ID: {snapshot_v1}")
    
    time.sleep(2)
    
    # Version 2: Price update
    print("\n💰 Version 2: Updating prices (10% discount)")
    spark.sql(f"""
        UPDATE {table_name}
        SET price = price * 0.9
        WHERE id IN (1, 2)
    """)
    
    spark.sql(f"SELECT * FROM {table_name}").show()
    
    snapshots_v2 = spark.sql(f"SELECT snapshot_id FROM {table_name}.snapshots").collect()
    snapshot_v2 = snapshots_v2[-1].snapshot_id
    print(f"   Snapshot ID: {snapshot_v2}")
    
    time.sleep(2)
    
    # Version 3: Add new product
    print("\n📦 Version 3: Adding new product")
    new_product = [(4, "Monitor", 300.0, 15)]
    df_new = spark.createDataFrame(new_product, ["id", "name", "price", "quantity"])
    df_new.writeTo(table_name).append()
    
    spark.sql(f"SELECT * FROM {table_name}").show()
    
    # Time travel queries
    print("\n⏰ Time Travel: Querying historical versions")
    print("\n--- Current version (Version 3) ---")
    spark.sql(f"SELECT * FROM {table_name}").show()
    
    print(f"\n--- Version 1 (Snapshot: {snapshot_v1}) ---")
    spark.sql(f"SELECT * FROM {table_name} VERSION AS OF {snapshot_v1}").show()
    
    print(f"\n--- Version 2 (Snapshot: {snapshot_v2}) ---")
    spark.sql(f"SELECT * FROM {table_name} VERSION AS OF {snapshot_v2}").show()
    
    # Show all snapshots
    print("\n📊 All Table Snapshots:")
    spark.sql(f"SELECT snapshot_id, committed_at, operation FROM {table_name}.snapshots").show(truncate=False)


def demo_schema_evolution(spark):
    """Demonstrate Iceberg schema evolution"""
    print("\n" + "="*70)
    print(" Demo 2: Schema Evolution with Iceberg")
    print("="*70)
    
    table_name = "demo.products_db.products_evolving"
    
    print(f"\n📝 Creating table with initial schema: {table_name}")
    spark.sql(f"DROP TABLE IF EXISTS {table_name}")
    
    # Initial schema
    initial_data = [
        (1, "Laptop", 1000.0),
        (2, "Mouse", 25.0)
    ]
    df_initial = spark.createDataFrame(initial_data, ["id", "name", "price"])
    df_initial.writeTo(table_name).using("iceberg").create()
    
    print("\n✅ Initial Schema:")
    spark.sql(f"DESCRIBE {table_name}").show()
    spark.sql(f"SELECT * FROM {table_name}").show()
    
    # Add new column
    print("\n➕ Adding new column: 'category'")
    spark.sql(f"ALTER TABLE {table_name} ADD COLUMN category string")
    
    print("\n✅ Updated Schema:")
    spark.sql(f"DESCRIBE {table_name}").show()
    
    # Insert data with new column
    print("\n📝 Inserting data with new column")
    new_data = [(3, "Keyboard", 75.0, "Electronics")]
    df_new = spark.createDataFrame(new_data, ["id", "name", "price", "category"])
    df_new.writeTo(table_name).append()
    
    print("\n✅ Data with new column (old rows have NULL):")
    spark.sql(f"SELECT * FROM {table_name}").show()
    
    # Update old rows
    print("\n🔄 Updating old rows with category")
    spark.sql(f"""
        UPDATE {table_name}
        SET category = 'Electronics'
        WHERE category IS NULL
    """)
    
    print("\n✅ All rows now have category:")
    spark.sql(f"SELECT * FROM {table_name}").show()
    
    # Add another column
    print("\n➕ Adding column: 'in_stock' (boolean)")
    spark.sql(f"ALTER TABLE {table_name} ADD COLUMN in_stock boolean")
    
    # Set default value for existing rows
    spark.sql(f"""
        UPDATE {table_name}
        SET in_stock = true
        WHERE in_stock IS NULL
    """)
    
    print("\n✅ Final Schema:")
    spark.sql(f"DESCRIBE {table_name}").show()
    spark.sql(f"SELECT * FROM {table_name}").show()
    
    # Rename column
    print("\n✏️ Renaming column: 'name' → 'product_name'")
    spark.sql(f"ALTER TABLE {table_name} RENAME COLUMN name TO product_name")
    
    print("\n✅ After rename:")
    spark.sql(f"DESCRIBE {table_name}").show()
    spark.sql(f"SELECT * FROM {table_name}").show()


def demo_partitioning(spark):
    """Demonstrate Iceberg partitioning"""
    print("\n" + "="*70)
    print(" Demo 3: Table Partitioning")
    print("="*70)
    
    table_name = "demo.products_db.products_partitioned"
    
    print(f"\n📝 Creating partitioned table: {table_name}")
    spark.sql(f"DROP TABLE IF EXISTS {table_name}")
    
    # Create partitioned table
    spark.sql(f"""
        CREATE TABLE {table_name} (
            id INT,
            name STRING,
            price DOUBLE,
            quantity INT,
            category STRING,
            sale_date DATE
        )
        USING iceberg
        PARTITIONED BY (category, days(sale_date))
    """)
    
    # Insert data with different categories and dates
    data = [
        (1, "Laptop", 1000.0, 10, "Electronics", "2024-01-15"),
        (2, "Mouse", 25.0, 50, "Electronics", "2024-01-20"),
        (3, "Desk", 300.0, 5, "Furniture", "2024-02-01"),
        (4, "Chair", 200.0, 8, "Furniture", "2024-02-15"),
        (5, "Monitor", 400.0, 15, "Electronics", "2024-03-01"),
        (6, "Bookshelf", 150.0, 10, "Furniture", "2024-03-10")
    ]
    
    df = spark.createDataFrame(data, ["id", "name", "price", "quantity", "category", "sale_date"])
    df.writeTo(table_name).append()
    
    print("\n✅ Data inserted into partitioned table:")
    spark.sql(f"SELECT * FROM {table_name} ORDER BY sale_date").show()
    
    # Show partition information
    print("\n📊 Partition Information:")
    spark.sql(f"SELECT partition, record_count, file_count FROM {table_name}.partitions").show(truncate=False)
    
    # Query specific partition
    print("\n🔍 Query specific partition (Electronics only):")
    spark.sql(f"SELECT * FROM {table_name} WHERE category = 'Electronics'").show()
    
    print("\n💡 Benefits of partitioning:")
    print("   - Faster queries (partition pruning)")
    print("   - Better organization")
    print("   - Efficient data management")


def main():
    """Run all advanced demos"""
    print("="*70)
    print(" Apache Iceberg Advanced Features Demo")
    print("="*70)
    print()
    print("This demo showcases:")
    print("  1. Time Travel - Query historical versions of data")
    print("  2. Schema Evolution - Add/modify columns without downtime")
    print("  3. Partitioning - Organize data for better performance")
    print()
    
    spark = create_spark_session()
    
    try:
        # Run demos
        demo_time_travel(spark)
        demo_schema_evolution(spark)
        demo_partitioning(spark)
        
        print("\n" + "="*70)
        print(" ✅ All Advanced Demos Complete!")
        print("="*70)
        print()
        print("Key Takeaways:")
        print("  • Time Travel allows auditing and recovering historical data")
        print("  • Schema Evolution enables adapting to changing requirements")
        print("  • Partitioning improves query performance dramatically")
        print()
        print("These features make Iceberg ideal for:")
        print("  - Data lakes with evolving schemas")
        print("  - Regulatory compliance and auditing")
        print("  - Large-scale analytics workloads")
        print()
        
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
