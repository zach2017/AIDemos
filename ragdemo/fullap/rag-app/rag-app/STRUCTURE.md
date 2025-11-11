# Project Structure

```
rag-app/
│
├── 📄 docker-compose.yml          # Main orchestration file - defines all services
├── 📄 README.md                   # Comprehensive documentation
├── 📄 QUICKSTART.md               # Quick start guide for impatient users
├── 📄 TESTING.md                  # Testing guide and verification steps
├── 📄 .env.example                # Example environment variables
├── 📄 .gitignore                  # Git ignore file
│
├── 🚀 start.sh                    # Convenience script to start the application
├── 🛑 stop.sh                     # Convenience script to stop the application
│
├── 📁 data/                       # Sample documents directory
│   ├── artificial_intelligence.txt    # AI concepts and terminology
│   ├── python_programming.txt         # Python language guide
│   └── docker_guide.txt               # Docker and containerization guide
│
├── 📁 streamlit-app/              # Streamlit interface (Port 8501)
│   ├── 📄 Dockerfile              # Docker image definition
│   ├── 📄 requirements.txt        # Python dependencies
│   ├── 📄 app.py                  # Main Streamlit application
│   │
│   └── 📁 utils/                  # Utility modules
│       ├── 📄 __init__.py         # Package initializer
│       ├── 📄 document_loader.py  # Document loading and chunking
│       ├── 📄 vectorstore.py      # ChromaDB interface
│       └── 📄 rag_chain.py        # RAG workflow logic
│
└── 📁 web-app/                    # Web interface (Port 5000)
    ├── 📄 Dockerfile              # Docker image definition
    ├── 📄 requirements.txt        # Python dependencies
    ├── 📄 server.py               # Flask backend server
    │
    └── 📁 static/                 # Frontend files
        ├── 📄 index.html          # Main HTML page
        ├── 📄 style.css           # Styles and layout
        └── 📄 script.js           # JavaScript logic
```

## Component Descriptions

### Root Level Files

- **docker-compose.yml**: Orchestrates 5 services (Ollama, ChromaDB, Streamlit, Web App, Model Init)
- **README.md**: Full documentation with setup, usage, troubleshooting
- **QUICKSTART.md**: 3-step guide to get started immediately
- **TESTING.md**: Comprehensive testing guide
- **.env.example**: Template for environment variables
- **.gitignore**: Files to exclude from version control
- **start.sh**: Automated startup with helpful info
- **stop.sh**: Clean shutdown script

### Data Directory

Contains sample documents for testing:
- AI and machine learning concepts
- Python programming guide
- Docker and containerization guide

Add your own .txt, .md, or .pdf files here!

### Streamlit App

**Purpose**: Rich, interactive UI with file upload and document management

**Components**:
- `app.py`: Main interface with chat, document upload, status indicators
- `utils/document_loader.py`: Loads and splits documents into chunks
- `utils/vectorstore.py`: Manages ChromaDB vector store operations
- `utils/rag_chain.py`: Implements retrieval and generation logic

**Features**:
- File upload (TXT, MD, PDF)
- Chat interface with history
- Source display
- Visual status indicators
- Document management

### Web App

**Purpose**: Clean HTML/JS interface with REST API

**Backend (server.py)**:
- Flask REST API
- Document management endpoints
- Query processing
- ChromaDB integration

**Frontend (static/)**:
- Modern, responsive design
- Real-time status updates
- Interactive chat interface
- Source citation display

**API Endpoints**:
- `GET /api/health`: Health check
- `POST /api/load-sample-data`: Load documents
- `POST /api/query`: Ask questions
- `GET /api/status`: System status
- `POST /api/clear`: Clear vector store

## Service Architecture

```
                    ┌─────────────┐
                    │   Docker    │
                    │   Network   │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
       ┌────▼────┐    ┌───▼────┐    ┌───▼────┐
       │ Ollama  │    │Chroma  │    │ Init   │
       │  (LLM)  │    │  DB    │    │Service │
       └────┬────┘    └───┬────┘    └────────┘
            │              │
       ┌────┴──────────────┴────┐
       │                         │
  ┌────▼────┐            ┌──────▼───┐
  │Streamlit│            │ Web App  │
  │  :8501  │            │  :5000   │
  └─────────┘            └──────────┘
       │                       │
       └───────┬───────────────┘
               │
         ┌─────▼─────┐
         │  Browser  │
         └───────────┘
```

## Data Flow

```
User Question
     │
     ▼
┌──────────────┐
│   Interface  │  (Streamlit or Web)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Vectorstore  │  Query ChromaDB for relevant docs
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  RAG Chain   │  Combine docs with question
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Ollama    │  Generate answer with LLaMA 2
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Response   │  Answer + Sources
└──────────────┘
```

## File Sizes (Approximate)

```
Code Files:           ~50 KB
Sample Data:          ~15 KB
Docker Images:        ~5 GB (after first run)
LLaMA 2 Model:        ~4 GB
ChromaDB Data:        Varies (depends on documents)
```

## Port Usage

- **5000**: Web App (Flask)
- **8501**: Streamlit App
- **8000**: ChromaDB
- **11434**: Ollama

## Volume Mounts

- `ollama_data`: Persistent model storage
- `chroma_data`: Persistent vector store
- `./data`: Shared document directory (host → containers)
- `./streamlit-app`: Hot reload for development
- `./web-app`: Hot reload for development

## Technology Stack

**Backend**:
- Python 3.11
- Flask (Web API)
- Streamlit (UI framework)
- ChromaDB (Vector database)
- Ollama (LLM inference)
- Sentence Transformers (Embeddings)

**Frontend**:
- HTML5
- CSS3 (with modern flexbox/grid)
- Vanilla JavaScript (no framework dependencies)

**Infrastructure**:
- Docker
- Docker Compose
- Linux containers

## Customization Points

**Easy to modify**:
- ✏️ Sample documents (add/remove from data/)
- ✏️ UI styling (edit style.css)
- ✏️ Prompts (edit rag_chain.py)
- ✏️ Chunk size (edit document_loader.py)
- ✏️ Number of results (edit query functions)

**Moderate effort**:
- 🔧 Switch LLM model (change docker-compose.yml)
- 🔧 Add file upload to web app
- 🔧 Custom embedding model
- 🔧 Additional API endpoints

**Advanced**:
- 🚀 Add authentication
- 🚀 Multi-user support
- 🚀 Production deployment
- 🚀 Kubernetes orchestration
- 🚀 Fine-tuned models

## Development Workflow

1. **Modify Code**: Edit files in streamlit-app/ or web-app/
2. **Auto Reload**: Changes are hot-reloaded (no rebuild needed)
3. **Rebuild Images**: Only needed for dependency changes
4. **Test**: Use both interfaces to verify changes
5. **Deploy**: Ready for production with minimal changes

## Next Steps

After understanding the structure:

1. 📖 Read QUICKSTART.md to run the app
2. 🧪 Follow TESTING.md to verify everything works
3. ✏️ Modify sample documents or add your own
4. 🎨 Customize the UI to your liking
5. 🚀 Build features specific to your use case

---

**Questions?** Check README.md for detailed documentation and troubleshooting!
