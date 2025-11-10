#!/usr/bin/env python3
"""
Interactive Query Script - Ask questions about products using RAG with Ollama
"""

import chromadb
import requests
import sys

CHROMA_HOST = "chroma"
CHROMA_PORT = 8000
OLLAMA_BASE_URL = "http://ollama:11434"


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


def query_products(question):
    """Query Chroma and generate answer with Ollama"""
    try:
        # Connect to Chroma
        chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = chroma_client.get_collection(name="products")
        
        # Generate query embedding
        query_embedding = generate_embeddings(question)
        
        # Search in Chroma
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        print("\n📦 Relevant Products Found:")
        print("-" * 60)
        
        context_docs = []
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"{i+1}. {metadata['name']} - ${metadata['price']}")
            print(f"   Stock: {metadata['stock']} | Category: {metadata['category']}")
            context_docs.append(doc)
        
        # Create context for LLM
        context = "\n\n".join(context_docs)
        
        # Generate answer with Ollama
        prompt = f"""Based on the following product information, provide a helpful and concise answer to the user's question.

Product Information:
{context}

User Question: {question}

Provide a brief, helpful response focusing on the most relevant products:"""
        
        print("\n🤖 AI Assistant Response:")
        print("-" * 60)
        
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
        print("-" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the demo has been initialized first by running: python /app/scripts/demo.py")


def main():
    print("="*60)
    print(" Interactive Product Query with RAG (Ollama + Chroma)")
    print("="*60)
    
    if len(sys.argv) > 1:
        # Question provided as command line argument
        question = " ".join(sys.argv[1:])
        query_products(question)
    else:
        # Interactive mode
        print("\nAsk questions about products (or 'quit' to exit)")
        print("Examples:")
        print("  - What products do you have for home office?")
        print("  - Show me electronics under $100")
        print("  - I need ergonomic furniture")
        print()
        
        while True:
            try:
                question = input("\n💬 Your question: ").strip()
                
                if not question:
                    continue
                    
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! 👋")
                    break
                
                query_products(question)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except EOFError:
                break


if __name__ == "__main__":
    main()
