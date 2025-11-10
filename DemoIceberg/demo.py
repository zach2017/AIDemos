#!/usr/bin/env python3
"""
Apache Iceberg Data Lake Demo with LocalStack S3, Chroma, and Ollama
"""

import os
import time
import boto3
import pandas as pd
from datetime import datetime
from pyspark.sql import SparkSession
import chromadb
import requests

# Configuration
S3_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
S3_BUCKET = "iceberg-warehouse"
CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "ollama")
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:11434"


def wait_for_services():
    """Wait for all services to be ready"""
    print("Waiting for services to be ready...")
    
    max_retries = 30
    
    # Wait for LocalStack
    for i in range(max_retries):
        try:
            response = requests.get(f"{S3_ENDPOINT}/_localstack/health")
            if response.status_code == 200:
                print("✓ LocalStack is ready")
                break
        except:
            pass
        time.sleep(2)
    
    # Wait for Chroma
    for i in range(max_retries):
        try:
            chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            print("✓ Chroma is ready")
            break
        except:
            pass
        time.sleep(2)
    
    # Wait for Ollama
    for i in range(max_retries):
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                print("✓ Ollama is ready")
                break
        except:
            pass
        time.sleep(2)
    
    time.sleep(3)


def setup_s3_bucket():
    """Create S3 bucket in LocalStack"""
    print("\n=== Setting up S3 Bucket ===")
    
    s3_client = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )
    
    try:
        s3_client.create_bucket(Bucket=S3_BUCKET)
        print(f"✓ Created S3 bucket: {S3_BUCKET}")
    except Exception as e:
        if 'BucketAlreadyOwnedByYou' in str(e):
            print(f"✓ S3 bucket already exists: {S3_BUCKET}")
        else:
            print(f"Note: {e}")
    
    return s3_client


def create_spark_session():
    """Create Spark session with Iceberg configuration"""
    print("\n=== Creating Spark Session ===")
    
    spark = SparkSession.builder \
        .appName("IcebergDemo") \
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
    print("✓ Spark session created")
    return spark


def create_sample_data():
    """Create sample product data"""
    return [
        {
            "product_id": 1,
            "name": "Laptop Pro 15",
            "category": "Electronics",
            "description": "High-performance laptop with 16GB RAM, 512GB SSD, and Intel Core i7 processor. Perfect for developers and content creators.",
            "price": 1299.99,
            "stock": 45,
            "created_at": "2024-01-15"
        },
        {
            "product_id": 2,
            "name": "Wireless Mouse",
            "category": "Electronics",
            "description": "Ergonomic wireless mouse with precision tracking and long battery life. Compatible with all major operating systems.",
            "price": 29.99,
            "stock": 150,
            "created_at": "2024-01-20"
        },
        {
            "product_id": 3,
            "name": "Standing Desk",
            "category": "Furniture",
            "description": "Adjustable height standing desk with electric motor. Promotes better posture and productivity. Weight capacity: 150 lbs.",
            "price": 499.99,
            "stock": 20,
            "created_at": "2024-02-01"
        },
        {
            "product_id": 4,
            "name": "Mechanical Keyboard",
            "category": "Electronics",
            "description": "RGB mechanical keyboard with cherry MX switches. Customizable lighting and programmable keys for gaming and productivity.",
            "price": 149.99,
            "stock": 75,
            "created_at": "2024-02-10"
        },
        {
            "product_id": 5,
            "name": "Office Chair",
            "category": "Furniture",
            "description": "Ergonomic office chair with lumbar support, adjustable armrests, and breathable mesh back. Supports up to 300 lbs.",
            "price": 299.99,
            "stock": 30,
            "created_at": "2024-02-15"
        },
        {
            "product_id": 6,
            "name": "USB-C Hub",
            "category": "Electronics",
            "description": "7-in-1 USB-C hub with HDMI, USB 3.0 ports, SD card reader, and 100W power delivery. Ideal for laptops with limited ports.",
            "price": 49.99,
            "stock": 200,
            "created_at": "2024-03-01"
        }
    ]


def create_iceberg_table(spark):
    """Create and populate Iceberg table"""
    print("\n=== Creating Iceberg Table ===")
    
    # Create database
    spark.sql("CREATE DATABASE IF NOT EXISTS demo.products_db")
    print("✓ Created database: demo.products_db")
    
    # Drop table if exists
    spark.sql("DROP TABLE IF EXISTS demo.products_db.products")
    
    # Create sample data
    data = create_sample_data()
    df = spark.createDataFrame(data)
    
    # Write to Iceberg table
    df.writeTo("demo.products_db.products") \
        .using("iceberg") \
        .createOrReplace()
    
    print("✓ Created and populated Iceberg table: demo.products_db.products")
    
    # Show table contents
    result_df = spark.sql("SELECT * FROM demo.products_db.products")
    print(f"\n✓ Table contains {result_df.count()} records")
    print("\nSample data:")
    result_df.show(truncate=False)
    
    return result_df


def pull_ollama_model():
    """Pull the embedding model if not available"""
    print("\n=== Setting up Ollama Model ===")
    
    model_name = "nomic-embed-text"
    
    try:
        # Check if model exists
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        models = response.json().get('models', [])
        model_exists = any(model_name in model.get('name', '') for model in models)
        
        if not model_exists:
            print(f"Pulling {model_name} model (this may take a few minutes)...")
            pull_response = requests.post(
                f"{OLLAMA_BASE_URL}/api/pull",
                json={"name": model_name},
                stream=True
            )
            
            for line in pull_response.iter_lines():
                if line:
                    print(".", end="", flush=True)
            print()
        
        print(f"✓ Model {model_name} is ready")
        
        # Also pull a chat model for Q&A
        chat_model = "llama3.2:1b"
        models = response.json().get('models', [])
        chat_exists = any(chat_model in model.get('name', '') for model in models)
        
        if not chat_exists:
            print(f"\nPulling {chat_model} model for Q&A...")
            pull_response = requests.post(
                f"{OLLAMA_BASE_URL}/api/pull",
                json={"name": chat_model},
                stream=True
            )
            
            for line in pull_response.iter_lines():
                if line:
                    print(".", end="", flush=True)
            print()
        
        print(f"✓ Model {chat_model} is ready")
        
    except Exception as e:
        print(f"Note: {e}")


def generate_embeddings(text):
    """Generate embeddings using Ollama"""
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )
    return response.json()['embedding']


def setup_chroma_collection(products_df):
    """Create Chroma collection and add product embeddings"""
    print("\n=== Setting up Chroma Vector Database ===")
    
    # Initialize Chroma client
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    
    # Delete collection if exists
    try:
        chroma_client.delete_collection(name="products")
    except:
        pass
    
    # Create collection
    collection = chroma_client.create_collection(
        name="products",
        metadata={"description": "Product catalog with embeddings"}
    )
    
    print("✓ Created Chroma collection: products")
    
    # Convert to pandas for easier processing
    products = products_df.toPandas()
    
    # Generate embeddings and add to Chroma
    print("Generating embeddings and storing in Chroma...")
    
    for idx, row in products.iterrows():
        # Create text for embedding
        text = f"{row['name']}: {row['description']} Category: {row['category']} Price: ${row['price']}"
        
        # Generate embedding
        embedding = generate_embeddings(text)
        
        # Add to collection
        collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "product_id": int(row['product_id']),
                "name": row['name'],
                "category": row['category'],
                "price": float(row['price']),
                "stock": int(row['stock'])
            }],
            ids=[f"product_{row['product_id']}"]
        )
        
        print(f"  ✓ Added {row['name']}")
    
    print(f"\n✓ Stored {len(products)} products in Chroma with embeddings")
    
    return collection


def query_with_context(collection, query_text):
    """Query Chroma and generate answer with Ollama"""
    print(f"\n=== Query: {query_text} ===")
    
    # Generate query embedding
    query_embedding = generate_embeddings(query_text)
    
    # Search in Chroma
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    
    print("\nTop matching products:")
    context_docs = []
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f"\n{i+1}. {metadata['name']} (${metadata['price']})")
        print(f"   Stock: {metadata['stock']} | Category: {metadata['category']}")
        context_docs.append(doc)
    
    # Create context for LLM
    context = "\n\n".join(context_docs)
    
    # Generate answer with Ollama
    prompt = f"""Based on the following product information, answer the user's question.

Product Information:
{context}

User Question: {query_text}

Answer:"""
    
    print("\n" + "="*60)
    print("AI Response:")
    print("="*60)
    
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": "llama3.2:1b",
            "prompt": prompt,
            "stream": False
        }
    )
    
    answer = response.json()['response']
    print(answer)
    print("="*60)
    
    return answer


def run_demo():
    """Run the complete demo"""
    print("="*70)
    print(" Apache Iceberg + LocalStack S3 + Chroma + Ollama Demo")
    print("="*70)
    
    # Wait for services
    wait_for_services()
    
    # Setup S3
    s3_client = setup_s3_bucket()
    
    # Create Spark session
    spark = create_spark_session()
    
    # Create Iceberg table
    products_df = create_iceberg_table(spark)
    
    # Setup Ollama
    pull_ollama_model()
    
    # Setup Chroma with embeddings
    collection = setup_chroma_collection(products_df)
    
    # Run sample queries
    print("\n" + "="*70)
    print(" Running Sample Queries")
    print("="*70)
    
    queries = [
        "What laptops do you have for developers?",
        "I need furniture for my home office under $500",
        "Show me electronics accessories"
    ]
    
    for query in queries:
        query_with_context(collection, query)
        time.sleep(1)
    
    # Show Iceberg table statistics
    print("\n" + "="*70)
    print(" Iceberg Table Statistics")
    print("="*70)
    
    spark.sql("SELECT category, COUNT(*) as count, AVG(price) as avg_price FROM demo.products_db.products GROUP BY category").show()
    
    print("\n" + "="*70)
    print(" Demo Complete!")
    print("="*70)
    print("\nYou can now:")
    print("1. Query the Iceberg table using Spark SQL")
    print("2. Search products using Chroma vector similarity")
    print("3. Ask questions with Ollama and get contextual answers")
    print("\nTo interact with the demo:")
    print("  docker exec -it iceberg-app python /app/scripts/demo.py")
    
    spark.stop()


if __name__ == "__main__":
    run_demo()
