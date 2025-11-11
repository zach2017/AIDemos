from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import requests

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

# Initialize ChromaDB client
chroma_client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=CHROMA_PORT,
    settings=Settings(anonymized_telemetry=False)
)

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Get or create collection
collection = chroma_client.get_or_create_collection(
    name="rag_documents",
    metadata={"hnsw:space": "cosine"}
)

@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('static', 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'ollama_url': OLLAMA_URL,
        'chroma_host': CHROMA_HOST,
        'chroma_port': CHROMA_PORT
    })

@app.route('/api/load-sample-data', methods=['POST'])
def load_sample_data():
    """Load sample data into the vector store."""
    try:
        data_dir = '/app/data'
        documents = []
        
        # Load all text files from data directory
        for filename in os.listdir(data_dir):
            if filename.endswith(('.txt', '.md')):
                file_path = os.path.join(data_dir, filename)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Split into chunks (simple splitting)
                    chunk_size = 1000
                    for i in range(0, len(content), chunk_size):
                        chunk = content[i:i + chunk_size]
                        if chunk.strip():
                            documents.append({
                                'content': chunk,
                                'source': filename,
                                'chunk_id': i // chunk_size
                            })
        
        if documents:
            # Generate embeddings
            contents = [doc['content'] for doc in documents]
            embeddings = embedding_model.encode(contents).tolist()
            
            # Add to collection
            ids = [f"doc_{i}" for i in range(len(documents))]
            metadatas = [{'source': doc['source'], 'chunk_id': doc['chunk_id']} for doc in documents]
            
            collection.add(
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
                ids=ids
            )
            
            return jsonify({
                'success': True,
                'message': f'Loaded {len(documents)} document chunks',
                'count': len(documents)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No documents found in data directory'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading data: {str(e)}'
        }), 500

@app.route('/api/query', methods=['POST'])
def query():
    """Query the RAG system."""
    try:
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({
                'success': False,
                'message': 'Question is required'
            }), 400
        
        # Check if collection has documents
        if collection.count() == 0:
            return jsonify({
                'success': False,
                'message': 'No documents loaded. Please load sample data first.'
            }), 400
        
        # Retrieve relevant documents
        query_embedding = embedding_model.encode(question).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        if not results['documents'][0]:
            return jsonify({
                'success': True,
                'answer': "I couldn't find any relevant information to answer your question.",
                'sources': []
            })
        
        # Build context
        context = "\n\n".join([
            f"Document {i+1}:\n{doc}"
            for i, doc in enumerate(results['documents'][0])
        ])
        
        # Create prompt
        prompt = f"""You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {question}

Instructions:
- Answer the question based ONLY on the information provided in the context above.
- If the context doesn't contain enough information to answer the question, say so.
- Be concise and accurate.
- Do not make up information that is not in the context.

Answer:"""
        
        # Generate answer using Ollama
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', 'No response generated.')
            
            return jsonify({
                'success': True,
                'answer': answer,
                'sources': results['documents'][0]
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Error from Ollama: {response.status_code}'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing query: {str(e)}'
        }), 500

@app.route('/api/clear', methods=['POST'])
def clear_collection():
    """Clear the vector store."""
    try:
        global collection
        chroma_client.delete_collection(name="rag_documents")
        collection = chroma_client.get_or_create_collection(
            name="rag_documents",
            metadata={"hnsw:space": "cosine"}
        )
        return jsonify({
            'success': True,
            'message': 'Vector store cleared successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error clearing vector store: {str(e)}'
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Get system status."""
    try:
        doc_count = collection.count()
        return jsonify({
            'success': True,
            'document_count': doc_count,
            'collection_ready': doc_count > 0
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting status: {str(e)}'
        }), 500

if __name__ == '__main__':
    print(f"Starting Flask server...")
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"ChromaDB: {CHROMA_HOST}:{CHROMA_PORT}")
    app.run(host='0.0.0.0', port=5000, debug=True)
