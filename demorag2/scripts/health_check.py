#!/usr/bin/env python3
"""
Health Check Script - Verify all services are running
"""

import time
import requests
import chromadb
import boto3
from pyspark.sql import SparkSession

def check_localstack():
    """Check if LocalStack is healthy"""
    try:
        response = requests.get("http://localstack:4566/_localstack/health", timeout=5)
        if response.status_code == 200:
            print("✅ LocalStack S3: Running")
            return True
    except:
        pass
    print("❌ LocalStack S3: Not responding")
    return False


def check_chroma():
    """Check if Chroma is healthy"""
    try:
        client = chromadb.HttpClient(host="chroma", port=8000)
        client.heartbeat()
        print("✅ Chroma Vector DB: Running")
        return True
    except:
        print("❌ Chroma Vector DB: Not responding")
        return False


def check_ollama():
    """Check if Ollama is healthy"""
    try:
        response = requests.get("http://ollama:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama: Running ({len(models)} models loaded)")
            for model in models:
                print(f"   - {model['name']}")
            return True
    except:
        pass
    print("❌ Ollama: Not responding")
    return False


def check_s3_bucket():
    """Check if S3 bucket exists"""
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url='http://localstack:4566',
            aws_access_key_id='test',
            aws_secret_access_key='test',
            region_name='us-east-1'
        )
        buckets = s3_client.list_buckets()
        bucket_names = [b['Name'] for b in buckets['Buckets']]
        if 'iceberg-warehouse' in bucket_names:
            print("✅ S3 Bucket 'iceberg-warehouse': Created")
            return True
        else:
            print("⚠️  S3 Bucket 'iceberg-warehouse': Not found (run demo.py to create)")
            return False
    except Exception as e:
        print(f"❌ S3 Bucket check failed: {e}")
        return False


def check_chroma_collection():
    """Check if Chroma collection exists"""
    try:
        client = chromadb.HttpClient(host="chroma", port=8000)
        collections = client.list_collections()
        if any(c.name == 'products' for c in collections):
            collection = client.get_collection('products')
            count = collection.count()
            print(f"✅ Chroma Collection 'products': {count} documents")
            return True
        else:
            print("⚠️  Chroma Collection 'products': Not found (run demo.py to create)")
            return False
    except Exception as e:
        print(f"❌ Chroma collection check failed: {e}")
        return False


def main():
    print("="*60)
    print(" Iceberg Demo - Health Check")
    print("="*60)
    print()
    
    checks = [
        ("LocalStack", check_localstack),
        ("Chroma", check_chroma),
        ("Ollama", check_ollama),
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append(result)
        print()
    
    # Additional checks
    print("Additional Checks:")
    print("-" * 60)
    check_s3_bucket()
    check_chroma_collection()
    
    print()
    print("="*60)
    if all(results):
        print("✅ All core services are healthy!")
        print()
        print("Next steps:")
        print("  1. Run demo: docker exec -it iceberg-app python /app/scripts/demo.py")
        print("  2. Query: docker exec -it iceberg-app python /app/scripts/query.py")
    else:
        print("⚠️  Some services are not responding")
        print()
        print("Try:")
        print("  1. Check if containers are running: docker-compose ps")
        print("  2. View logs: docker-compose logs")
        print("  3. Restart services: docker-compose restart")
    print("="*60)


if __name__ == "__main__":
    main()
