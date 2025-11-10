#!/usr/bin/env python3
"""
Simple Data Ingestion Example - Add new products to Iceberg table
"""

import sys
from pyspark.sql import SparkSession
from datetime import datetime

S3_ENDPOINT = "http://localstack:4566"
S3_BUCKET = "iceberg-warehouse"


def create_spark_session():
    """Create Spark session"""
    spark = SparkSession.builder \
        .appName("IcebergIngestion") \
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


def add_product(spark, product_data):
    """Add a new product to the Iceberg table"""
    table_name = "demo.products_db.products"
    
    try:
        # Check if table exists
        spark.sql(f"SELECT * FROM {table_name} LIMIT 1")
        
        # Get next product ID
        max_id = spark.sql(f"SELECT MAX(product_id) as max_id FROM {table_name}").collect()[0].max_id
        next_id = max_id + 1 if max_id else 1
        
        # Create DataFrame with new product
        product_data['product_id'] = next_id
        product_data['created_at'] = datetime.now().strftime("%Y-%m-%d")
        
        df = spark.createDataFrame([product_data])
        
        # Append to table
        df.writeTo(table_name).append()
        
        print(f"✅ Added product: {product_data['name']} (ID: {next_id})")
        
        # Show updated table
        print("\n📊 Updated Products Table:")
        spark.sql(f"SELECT * FROM {table_name} ORDER BY product_id DESC LIMIT 5").show(truncate=False)
        
        return next_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure to run the demo first: python /app/scripts/demo.py")
        return None


def interactive_add():
    """Interactive mode to add products"""
    spark = create_spark_session()
    
    print("="*60)
    print(" Add New Product to Iceberg Table")
    print("="*60)
    print()
    
    try:
        name = input("Product Name: ").strip()
        if not name:
            print("Product name is required!")
            return
        
        category = input("Category (Electronics/Furniture): ").strip() or "Electronics"
        description = input("Description: ").strip() or f"{name} - Great product!"
        
        try:
            price = float(input("Price ($): ").strip())
        except ValueError:
            print("Invalid price, using default: $99.99")
            price = 99.99
        
        try:
            stock = int(input("Stock Quantity: ").strip())
        except ValueError:
            print("Invalid stock, using default: 10")
            stock = 10
        
        product_data = {
            "name": name,
            "category": category,
            "description": description,
            "price": price,
            "stock": stock
        }
        
        print("\n" + "-"*60)
        print("Adding product...")
        print("-"*60)
        
        add_product(spark, product_data)
        
    finally:
        spark.stop()


def batch_add():
    """Add predefined products"""
    spark = create_spark_session()
    
    print("="*60)
    print(" Batch Adding Sample Products")
    print("="*60)
    print()
    
    products = [
        {
            "name": "Webcam HD",
            "category": "Electronics",
            "description": "1080p webcam with built-in microphone and auto-focus. Perfect for video calls and streaming.",
            "price": 79.99,
            "stock": 40
        },
        {
            "name": "Desk Lamp",
            "category": "Furniture",
            "description": "Adjustable LED desk lamp with multiple brightness levels and color temperatures.",
            "price": 45.99,
            "stock": 60
        },
        {
            "name": "External SSD 1TB",
            "category": "Electronics",
            "description": "Portable external SSD with USB 3.2 Gen 2 for fast data transfer. Compact and durable.",
            "price": 89.99,
            "stock": 35
        }
    ]
    
    try:
        for product in products:
            add_product(spark, product)
            print()
        
        print("="*60)
        print("✅ Batch ingestion complete!")
        print("="*60)
        
    finally:
        spark.stop()


def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        batch_add()
    else:
        interactive_add()


if __name__ == "__main__":
    main()
