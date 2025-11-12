import os
import shutil
import logging
from pathlib import Path
from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename

# Import langchain components
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- Configuration ---
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'txt', 'md', 'pdf', 'docx', 'csv'} # You can expand this

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'super-secret-key-change-me' # Required for flash messages
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Helper Functions ---

def allowed_file(filename):
    """Checks if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_text_files(file_paths):
    """Loads text content from a list of file paths."""
    logs = []
    docs = []
    for fp in file_paths:
        p = Path(fp)
        try:
            # Simple text loader (you might need specific loaders for PDF, DOCX etc.)
            # For simplicity, this example just reads text.
            # For PDF, use: from langchain_community.document_loaders import PyPDFLoader
            # For DOCX, use: from langchain_community.document_loaders import Docx2txtLoader
            if p.suffix.lower() == '.txt' or p.suffix.lower() == '.md' or p.suffix.lower() == '.csv':
                text = p.read_text(encoding="utf-8", errors="ignore")
                docs.append(Document(page_content=text, metadata={"source": str(p.name)}))
                logs.append(f"[INFO] Loaded text from: {p.name}")
            else:
                logs.append(f"[WARN] Skipping file with unhandled extension: {p.name}. (This demo only handles .txt, .md, .csv)")
        except Exception as e:
            logs.append(f"[ERROR] Failed to load {p.name}: {e}")
            
    return docs, logs

def run_ingestion(files, persist_dir, collection_name, reset, chunk_size, chunk_overlap):
    """
    Runs the full ingestion pipeline based on form inputs.
    Returns a list of log messages.
    """
    logs = []
    
    try:
        persist_path = Path(persist_dir)
        if reset and persist_path.exists():
            logs.append(f"[INFO] Resetting Chroma directory: {persist_dir}")
            shutil.rmtree(persist_dir)

        logs.append("[INFO] Loading documents from uploaded files…")
        raw_docs, load_logs = load_text_files(files)
        logs.extend(load_logs)
        
        if not raw_docs:
            logs.append("[ERROR] No valid documents were loaded. Exiting.")
            return logs, False

        logs.append("[INFO] Splitting into chunks…")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        chunks = splitter.split_documents(raw_docs)
        logs.append(f"[INFO] Total chunks created: {len(chunks)}")
        if not chunks:
            logs.append("[ERROR] No chunks were created from the documents. Check file content and chunk settings.")
            return logs, False

        logs.append("[INFO] Initializing local embeddings (all-MiniLM-L6-v2)…")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        if persist_path.exists():
            logs.append("[INFO] Existing DB found. Adding documents…")
            vectordb = Chroma(
                persist_directory=str(persist_path),
                collection_name=collection_name,
                embedding_function=embeddings,
            )
            vectordb.add_documents(chunks)
        
        else:
            logs.append("[INFO] Creating new DB…")
            Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=str(persist_path),
                collection_name=collection_name,
            )

        logs.append(f"[DONE] Chroma DB ready at: {persist_dir} (collection: {collection_name})")
        return logs, True

    except Exception as e:
        logs.append(f"[FATAL_ERROR] An unexpected error occurred: {e}")
        logging.exception("Ingestion failed") # Logs full traceback to server console
        return logs, False
    finally:
        # --- Cleanup: Remove temporary files ---
        logs.append("[INFO] Cleaning up temporary files…")
        for f in files:
            try:
                os.remove(f)
            except Exception as e:
                logs.append(f"[WARN] Could not remove temp file {f}: {e}")

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # --- 1. Get Form Data ---
        persist_dir = request.form.get('persist', './chroma_db').strip()
        collection_name = request.form.get('collection', 'demo').strip()
        chunk_size = int(request.form.get('chunk_size', 800))
        chunk_overlap = int(request.form.get('chunk_overlap', 120))
        reset = 'reset' in request.form
        
        # --- 2. Handle File Uploads ---
        uploaded_files = request.files.getlist('files')
        saved_file_paths = []
        
        if not uploaded_files or all(f.filename == '' for f in uploaded_files):
            flash('No files selected for uploading.', 'error')
            return redirect(url_for('index'))

        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                saved_file_paths.append(filepath)
            elif file:
                flash(f'File type not allowed: {file.filename}', 'warning')

        if not saved_file_paths:
            flash('No valid files were uploaded.', 'error')
            return redirect(url_for('index'))

        # --- 3. Run Ingestion ---
        flash('Starting ingestion process...', 'info')
        logs, success = run_ingestion(
            files=saved_file_paths,
            persist_dir=persist_dir,
            collection_name=collection_name,
            reset=reset,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # --- 4. Render Result ---
        # We pass logs and status back to the template
        return render_template(
            'index.html', 
            logs=logs, 
            success=success,
            # Pass back form values to repopulate
            persist=persist_dir,
            collection=collection_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            reset=reset
        )

    # --- GET Request: Show the form ---
    return render_template(
        'index.html',
        # Default values
        persist='./chroma_db',
        collection='demo',
        chunk_size=800,
        chunk_overlap=120,
        reset=False
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)