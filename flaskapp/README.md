# Document Embeddings Builder & Query System - Flask Web App

A modern web interface for building vector embeddings from text documents, storing them in a Chroma database, and querying them with optional RAG (Retrieval-Augmented Generation) using Ollama.

## Features

- 📤 **Drag & Drop Upload** - Easy file upload with drag-and-drop support
- 🎨 **Beautiful UI** - Modern tabbed interface styled with TailwindCSS
- ⚙️ **Full Configuration** - All command-line options available in the web UI
- 📊 **Real-time Feedback** - Progress indicators and detailed results
- 🗂️ **Multiple Formats** - Support for TXT, MD, CSV, JSON, LOG, PY, JS, HTML, CSS files
- 🔍 **Semantic Search** - Query your documents using natural language
- 🤖 **Ollama Integration** - Optional RAG with local LLMs (Llama2, Mistral, etc.)
- 🐳 **Docker Support** - Complete Docker Compose setup with Ollama

## Quick Start with Docker (Recommended)

### One-Command Setup

```bash
# Run the setup script
./setup-ollama.sh
```

This will:
1. Start both the Flask app and Ollama services
2. Let you choose and install an LLM model
3. Open the app at http://localhost:5000

### Manual Docker Setup

```bash
# Start services
docker-compose up -d

# Install a model
docker exec -it ollama_service ollama pull llama2

# Open http://localhost:5000
```

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for detailed Docker instructions.

## Installation (Without Docker)

### Prerequisites
- Python 3.8+
- (Optional) [Ollama](https://ollama.ai/) for RAG features

### Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **(Optional) Install Ollama** for RAG features
   - Download from [ollama.ai](https://ollama.ai/)
   - Pull a model: `ollama pull llama2`

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   ```
   http://localhost:5000
   ```

## Usage

### 1. Ingest Documents

The **Ingest Documents** tab allows you to upload and process documents:

1. **Upload Files**: 
   - Click or drag files into the upload area
   - Supports multiple files at once
   
2. **Configure Options**:
   - **Database Directory**: Where to store the Chroma database (default: `./chroma_db`)
   - **Collection Name**: Name for your document collection (default: `demo`)
   - **Chunk Size**: Characters per chunk (default: 800)
   - **Chunk Overlap**: Overlapping characters between chunks (default: 120)
   - **Reset Database**: Check to delete existing data before adding new documents
   
3. **Build Embeddings**: Click to process your documents

### 2. Query Documents

The **Query Database** tab allows you to search your ingested documents:

1. **Enter Your Query**: 
   - Type a natural language question
   - Example: "What are the main features of the product?"
   
2. **Configure Search**:
   - **Database Directory**: Same as used for ingestion
   - **Collection Name**: Same as used for ingestion
   - **Top K Results**: Number of relevant chunks to retrieve (default: 4)
   - **Ollama Model**: (Optional) LLM model name for RAG
   
3. **RAG Options**:
   - **Use Ollama for RAG**: Check to generate AI answers from retrieved context
   - Requires Ollama installed and a model pulled
   
4. **Search**: Click to query your documents

### Query Results

- **Without RAG**: Shows top matching document chunks ranked by relevance
- **With RAG**: Shows AI-generated answer + supporting document chunks

## Configuration Options Explained

### Ingest Options

- **Chunk Size**: Larger chunks preserve more context but may be less precise for retrieval. Smaller chunks are more precise but may lose context.
  - Small (400-600): Best for precise factual queries
  - Medium (800-1000): Balanced, good default
  - Large (1200-1500): Best for LLM context

- **Chunk Overlap**: Overlap helps maintain context across chunk boundaries.
  - Low (50-100): Less redundancy
  - Medium (120-200): Balanced, good default
  - High (200-300): Maximum context preservation

- **Reset Database**: Use this when you want to start fresh. Otherwise, new documents will be added to existing collections.

### Query Options

- **Top K**: Number of most relevant chunks to retrieve
  - k=2-3: Quick answers, less context
  - k=4-6: Balanced, good default
  - k=8-12: Maximum context for complex questions

- **Ollama Model**: Choose based on your needs
  - Fast: phi, neural-chat
  - Balanced: llama2, mistral
  - Quality: llama2:13b, llama2:70b

## File Support

The application accepts the following file types:
- Text files: `.txt`, `.md`, `.log`
- Code files: `.py`, `.js`, `.html`, `.css`
- Data files: `.csv`, `.json`

## How It Works

1. **Document Processing**: Uploaded files are read and converted to LangChain documents
2. **Text Splitting**: Documents are split into chunks using RecursiveCharacterTextSplitter
3. **Embedding Generation**: Chunks are embedded using HuggingFace's `all-MiniLM-L6-v2` model
4. **Vector Storage**: Embeddings are stored in a local Chroma database
5. **Ready for RAG**: The database can now be used for semantic search and retrieval-augmented generation

## API Endpoints

The Flask application exposes these REST endpoints:

### Document Ingestion
- **POST /upload** - Upload and process documents
  - Body: multipart/form-data with files and configuration options
  - Response: JSON with success status and processing details

### Document Querying
- **POST /query** - Query the database with optional RAG
  - Body: JSON with query parameters
  - Response: JSON with search results and optional LLM answer

### Utility
- **GET /collections** - List existing collections
  - Query: `persist_dir` (optional)
  - Response: JSON with list of collection names
  
- **GET /ollama/models** - List available Ollama models
  - Response: JSON with list of installed models
  
- **GET /health** - Health check endpoint
  - Response: JSON with service status

## Project Structure

```
.
├── app.py                 # Flask application
├── templates/
│   └── index.html        # Web interface
├── requirements.txt      # Python dependencies
├── uploads/              # Temporary file storage (auto-created)
└── chroma_db/           # Vector database storage (auto-created)
```

## Tips

- **Large Files**: The app supports files up to 100MB
- **Batch Processing**: Upload multiple files at once for efficient processing
- **Collection Organization**: Use different collection names to organize different document sets
- **Database Location**: You can specify different database directories for different projects

## Troubleshooting

**Issue**: First run is slow
- **Solution**: The first time you run the app, it needs to download the embedding model (~90MB). Subsequent runs will be faster.

**Issue**: Out of memory
- **Solution**: Reduce chunk size or process fewer files at once

**Issue**: Port already in use
- **Solution**: Change the port in `app.py` (line 119): `app.run(debug=True, host='0.0.0.0', port=5001)`

## Examples

### Basic Workflow

1. **Ingest Documents**:
   ```
   - Upload: company-docs.txt, product-specs.md, faq.txt
   - Collection: company_knowledge
   - Click "Build Embeddings"
   ```

2. **Query Without RAG** (Retrieval Only):
   ```
   - Query: "What are the product specifications?"
   - Top K: 4
   - Uncheck "Use Ollama for RAG"
   - Get: Relevant document chunks
   ```

3. **Query With RAG** (AI-Generated Answer):
   ```
   - Query: "Summarize the product features and benefits"
   - Ollama Model: llama2
   - Check "Use Ollama for RAG"
   - Get: AI answer + supporting documents
   ```

## Use Cases

- **Document Q&A**: Ask questions about your documentation
- **Knowledge Base**: Search company wikis, policies, procedures
- **Code Search**: Find relevant code snippets with explanations
- **Research**: Query academic papers or research documents
- **Customer Support**: RAG-powered answers from support docs

## Next Steps

Now that you have the system running:

1. **Build Your Vector Database**:
   - Upload your domain-specific documents
   - Organize into multiple collections by topic
   - Experiment with chunk sizes for your use case

2. **Explore Query Features**:
   - Test retrieval-only search for fact finding
   - Enable RAG for natural language answers
   - Compare different Ollama models

3. **Integrate Into Your Workflow**:
   - Use the REST API in your applications
   - Build chatbots with document-grounded responses
   - Create custom search interfaces
   - Automate Q&A systems

4. **Optimize Performance**:
   - Tune chunk sizes for your documents
   - Adjust top-k based on query complexity
   - Choose appropriate models for speed/quality tradeoff

## License

Free to use and modify for your projects!
