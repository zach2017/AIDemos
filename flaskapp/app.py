#!/usr/bin/env python3
"""
Flask web app for building embeddings from uploaded text files and storing them in Chroma DB.
Includes query functionality with optional Ollama integration for RAG.
"""

import os
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

try:
    from langchain_ollama import OllamaLLM
    OLLAMA_AVAILABLE = True
except ImportError:
    OllamaLLM = None
    OLLAMA_AVAILABLE = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

ALLOWED_EXTENSIONS = {'txt', 'md', 'csv', 'json', 'log', 'py', 'js', 'html', 'css'}

# Create upload folder if it doesn't exist
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_text_files(file_paths):
    docs = []
    for fp in file_paths:
        p = Path(fp).expanduser().resolve()
        if not p.exists() or not p.is_file():
            print(f"[WARN] Skipping missing file: {fp}")
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        docs.append(Document(page_content=text, metadata={"source": str(p.name)}))
    return docs

def process_documents(file_paths, persist_dir, collection_name, reset, chunk_size, chunk_overlap):
    """Process documents and store in Chroma DB"""
    try:
        persist_path = Path(persist_dir)
        
        if reset and persist_path.exists():
            shutil.rmtree(persist_path)
            
        raw_docs = load_text_files(file_paths)
        if not raw_docs:
            return {"success": False, "message": "No valid input files"}
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        chunks = splitter.split_documents(raw_docs)
        
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        if persist_path.exists():
            vectordb = Chroma(
                persist_directory=str(persist_path),
                collection_name=collection_name,
                embedding_function=embeddings,
            )
            vectordb.add_documents(chunks)
        else:
            Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=str(persist_path),
                collection_name=collection_name,
            )
        
        return {
            "success": True,
            "message": f"Successfully processed {len(raw_docs)} files into {len(chunks)} chunks",
            "chunks": len(chunks),
            "files": len(raw_docs)
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({"success": False, "message": "No files provided"})
    
    files = request.files.getlist('files[]')
    persist_dir = request.form.get('persist_dir', './chroma_db')
    collection_name = request.form.get('collection_name', 'demo')
    reset = request.form.get('reset') == 'true'
    chunk_size = int(request.form.get('chunk_size', 800))
    chunk_overlap = int(request.form.get('chunk_overlap', 120))
    
    if not files or files[0].filename == '':
        return jsonify({"success": False, "message": "No files selected"})
    
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_files.append(filepath)
    
    if not saved_files:
        return jsonify({"success": False, "message": "No valid files uploaded"})
    
    result = process_documents(saved_files, persist_dir, collection_name, reset, chunk_size, chunk_overlap)
    
    # Clean up uploaded files
    for filepath in saved_files:
        try:
            os.remove(filepath)
        except:
            pass
    
    return jsonify(result)

@app.route('/collections', methods=['GET'])
def list_collections():
    """List existing Chroma DB collections"""
    try:
        persist_dir = request.args.get('persist_dir', './chroma_db')
        persist_path = Path(persist_dir)
        
        if not persist_path.exists():
            return jsonify({"collections": []})
        
        # This is a simplified version - Chroma stores collections in subdirectories
        collections = []
        if persist_path.exists():
            collections = [d.name for d in persist_path.iterdir() if d.is_dir()]
        
        return jsonify({"collections": collections})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/query', methods=['POST'])
def query_database():
    """Query the Chroma database with optional Ollama RAG"""
    try:
        data = request.json
        query_text = data.get('query', '').strip()
        persist_dir = data.get('persist_dir', './chroma_db')
        collection_name = data.get('collection_name', 'demo')
        k = int(data.get('k', 4))
        ollama_model = data.get('ollama_model', '').strip()
        use_ollama = data.get('use_ollama', False)
        
        if not query_text:
            return jsonify({"success": False, "message": "Query text is required"})
        
        persist_path = Path(persist_dir)
        if not persist_path.exists():
            return jsonify({
                "success": False, 
                "message": f"Database directory not found: {persist_dir}. Please ingest documents first."
            })
        
        # Load embeddings and vector database
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectordb = Chroma(
            persist_directory=str(persist_path),
            collection_name=collection_name,
            embedding_function=embeddings,
        )
        
        # Perform similarity search
        docs = vectordb.similarity_search(query_text, k=k)
        
        if not docs:
            return jsonify({
                "success": True,
                "results": [],
                "message": "No matching documents found"
            })
        
        # Format results
        results = []
        for i, doc in enumerate(docs, 1):
            results.append({
                "rank": i,
                "source": doc.metadata.get("source", "unknown"),
                "content": doc.page_content,
                "preview": doc.page_content[:280].replace("\n", " ")
            })
        
        response_data = {
            "success": True,
            "results": results,
            "count": len(results)
        }
        
        # Optional Ollama RAG
        if use_ollama and ollama_model and OLLAMA_AVAILABLE:
            try:
                llm = OllamaLLM(model=ollama_model)
                context = "\n\n".join([
                    f"Source: {d.metadata.get('source', 'unknown')}\n{d.page_content}" 
                    for d in docs
                ])
                prompt = (
                    "You are a helpful assistant. Using only the CONTEXT below, answer the QUESTION clearly.\n\n"
                    f"QUESTION:\n{query_text}\n\nCONTEXT:\n{context}\n\n"
                    "If the answer cannot be found in the context, say you don't know."
                )
                answer = llm.invoke(prompt)
                response_data["ollama_answer"] = answer.strip()
                response_data["ollama_model"] = ollama_model
            except Exception as e:
                response_data["ollama_error"] = f"Ollama error: {str(e)}"
        elif use_ollama and not OLLAMA_AVAILABLE:
            response_data["ollama_error"] = "Ollama library not installed. Install langchain-ollama."
        elif use_ollama and not ollama_model:
            response_data["ollama_error"] = "No Ollama model specified."
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Query error: {str(e)}"})

@app.route('/ollama/models', methods=['GET'])
def list_ollama_models():
    """List available Ollama models"""
    try:
        if not OLLAMA_AVAILABLE:
            return jsonify({"models": [], "available": False})
        
        # Try to get available models from Ollama
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            models = [model['name'] for model in response.json().get('models', [])]
            return jsonify({"models": models, "available": True})
        else:
            return jsonify({"models": [], "available": False})
    except Exception:
        # Return some common models as defaults
        return jsonify({
            "models": ["llama2", "llama3", "mistral", "phi", "neural-chat"],
            "available": False,
            "message": "Cannot connect to Ollama. Using default model list."
        })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "ollama_available": OLLAMA_AVAILABLE
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
