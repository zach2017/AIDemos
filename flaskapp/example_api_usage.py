#!/usr/bin/env python3
"""
Example script demonstrating how to use the REST API programmatically.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"

def upload_documents(files_list, collection="demo", chunk_size=800, reset=False):
    """Upload and ingest documents via API"""
    url = f"{BASE_URL}/upload"
    
    # Prepare files
    files = []
    for file_path in files_list:
        files.append(('files[]', open(file_path, 'rb')))
    
    # Prepare form data
    data = {
        'persist_dir': './chroma_db',
        'collection_name': collection,
        'chunk_size': chunk_size,
        'chunk_overlap': 120,
        'reset': 'true' if reset else 'false'
    }
    
    # Send request
    response = requests.post(url, files=files, data=data)
    
    # Close files
    for _, file_obj in files:
        file_obj.close()
    
    return response.json()

def query_documents(query, collection="demo", k=4, use_ollama=False, model="llama2"):
    """Query the document database"""
    url = f"{BASE_URL}/query"
    
    payload = {
        'query': query,
        'persist_dir': './chroma_db',
        'collection_name': collection,
        'k': k,
        'use_ollama': use_ollama,
        'ollama_model': model if use_ollama else ''
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    
    return response.json()

def list_ollama_models():
    """List available Ollama models"""
    url = f"{BASE_URL}/ollama/models"
    response = requests.get(url)
    return response.json()

def health_check():
    """Check if the service is healthy"""
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    return response.json()

# Example Usage
if __name__ == "__main__":
    print("🚀 API Usage Example\n")
    
    # 1. Health Check
    print("1. Checking service health...")
    health = health_check()
    print(f"   Status: {health.get('status')}")
    print(f"   Ollama Available: {health.get('ollama_available')}\n")
    
    # 2. Upload Documents (uncomment to use)
    # print("2. Uploading documents...")
    # result = upload_documents(
    #     files_list=['document1.txt', 'document2.txt'],
    #     collection='my_docs',
    #     reset=True
    # )
    # if result.get('success'):
    #     print(f"   ✅ Success! Processed {result.get('files')} files into {result.get('chunks')} chunks\n")
    # else:
    #     print(f"   ❌ Error: {result.get('message')}\n")
    
    # 3. Query Without RAG
    print("3. Querying documents (retrieval only)...")
    query_result = query_documents(
        query="What is the main topic?",
        collection="demo",
        k=3,
        use_ollama=False
    )
    
    if query_result.get('success'):
        print(f"   Found {query_result.get('count')} results:")
        for doc in query_result.get('results', [])[:2]:  # Show first 2
            print(f"   [{doc['rank']}] {doc['source']}")
            print(f"       {doc['preview'][:100]}...\n")
    else:
        print(f"   ❌ Error: {query_result.get('message')}\n")
    
    # 4. Query With RAG (requires Ollama)
    print("4. Querying with RAG (AI answer)...")
    rag_result = query_documents(
        query="Summarize the main points",
        collection="demo",
        k=4,
        use_ollama=True,
        model="llama2"
    )
    
    if rag_result.get('success'):
        if rag_result.get('ollama_answer'):
            print(f"   🤖 AI Answer:\n   {rag_result['ollama_answer'][:200]}...\n")
        elif rag_result.get('ollama_error'):
            print(f"   ⚠️ {rag_result['ollama_error']}\n")
        
        print(f"   Based on {rag_result.get('count')} retrieved documents\n")
    else:
        print(f"   ❌ Error: {rag_result.get('message')}\n")
    
    # 5. List Available Models
    print("5. Available Ollama models...")
    models = list_ollama_models()
    if models.get('available'):
        print(f"   Models: {', '.join(models.get('models', []))}")
    else:
        print(f"   ⚠️ Ollama not available or no models installed")
    
    print("\n✨ Done!")
