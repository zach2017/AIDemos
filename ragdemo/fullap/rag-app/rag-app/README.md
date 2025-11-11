# RAG Q&A System with Docker

A complete, production-ready Retrieval-Augmented Generation (RAG) application with dual interfaces (Streamlit and Web), powered by local Ollama models and ChromaDB vector store.

## 🌟 Features

- **Dual User Interfaces**
  - Modern Streamlit application with rich UI
  - Clean HTML/JS web interface with REST API
- **Local AI Processing**
  - Uses Ollama with LLaMA 2 model (runs locally)
  - No external API keys required
- **Vector Database**
  - ChromaDB for efficient document storage and retrieval
  - Persistent storage across restarts
- **Easy Deployment**
  - Complete Docker orchestration
  - Single command to start all services
  - Automatic model downloading

## 📋 Prerequisites

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)
- At least 8GB of RAM (16GB recommended)
- 10GB free disk space for models and data

### Optional
- NVIDIA GPU with Docker GPU support for faster inference

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
# If you have the project as a zip file, extract it
unzip rag-app.zip
cd rag-app
```

### 2. Start the Application

```bash
docker-compose up -d
```

This single command will:
- Pull all necessary Docker images
- Start Ollama service
- Start ChromaDB vector database
- Download the LLaMA 2 model (this may take 5-10 minutes on first run)
- Start both Streamlit and Web applications

### 3. Wait for Model Download

The first time you run the application, Ollama needs to download the LLaMA 2 model (~4GB). Check the download progress:

```bash
docker-compose logs -f ollama-init
```

Wait until you see "Model ready!" message.

### 4. Access the Applications

Once everything is running:

- **Streamlit Interface**: http://localhost:8501
- **Web Interface**: http://localhost:5000
- **ChromaDB**: http://localhost:8000
- **Ollama**: http://localhost:11434

## 📱 Using the Applications

### Streamlit Interface (Port 8501)

1. **Load Data**
   - Click "📖 Load Sample Data" in the sidebar to load example documents
   - Or upload your own TXT, MD, or PDF files

2. **Ask Questions**
   - Type your question in the chat input
   - The system will retrieve relevant context and generate an answer
   - View source documents used for the answer

3. **Manage Data**
   - Clear the vector store with "🗑️ Clear Vector Store"
   - Upload new documents anytime

### Web Interface (Port 5000)

1. **Load Sample Data**
   - Click "📖 Load Sample Data" button
   - Wait for confirmation message

2. **Ask Questions**
   - Type your question in the text area
   - Click "Send" or press Enter
   - View answers with source citations

3. **System Status**
   - Check document count in the status bar
   - See system readiness status

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                           │
│  ┌──────────┐    ┌──────────┐    ┌─────────────┐       │
│  │  Ollama  │◄───│ Streamlit│◄───│  User       │       │
│  │  (LLM)   │    │   App    │    │  Browser    │       │
│  └────┬─────┘    └──────────┘    └─────────────┘       │
│       │                                                   │
│       │          ┌──────────┐    ┌─────────────┐       │
│       └─────────►│ Web App  │◄───│  User       │       │
│                  │ (Flask)  │    │  Browser    │       │
│                  └────┬─────┘    └─────────────┘       │
│                       │                                   │
│                       ▼                                   │
│                  ┌──────────┐                            │
│                  │ChromaDB  │                            │
│                  │ (Vector  │                            │
│                  │  Store)  │                            │
│                  └──────────┘                            │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Environment Variables

The docker-compose.yml file includes the following configurable environment variables:

- `OLLAMA_BASE_URL`: URL for Ollama service (default: http://ollama:11434)
- `CHROMA_HOST`: ChromaDB host (default: chromadb)
- `CHROMA_PORT`: ChromaDB port (default: 8000)

### GPU Support

If you have an NVIDIA GPU, uncomment the GPU configuration in docker-compose.yml:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

## 📊 Project Structure

```
rag-app/
├── docker-compose.yml          # Docker orchestration
├── README.md                   # This file
├── data/                       # Sample documents
│   ├── artificial_intelligence.txt
│   └── python_programming.txt
├── streamlit-app/             # Streamlit interface
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                 # Main application
│   └── utils/                 # Utility modules
│       ├── __init__.py
│       ├── document_loader.py # Document processing
│       ├── vectorstore.py     # ChromaDB interface
│       └── rag_chain.py       # RAG logic
└── web-app/                   # Web interface
    ├── Dockerfile
    ├── requirements.txt
    ├── server.py              # Flask server
    └── static/                # Frontend files
        ├── index.html
        ├── style.css
        └── script.js
```

## 🛠️ Management Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f streamlit-app
docker-compose logs -f web-app
docker-compose logs -f ollama
docker-compose logs -f chromadb
```

### Stop the Application

```bash
docker-compose down
```

### Stop and Remove All Data

```bash
docker-compose down -v
```

### Restart a Specific Service

```bash
docker-compose restart streamlit-app
docker-compose restart web-app
```

### Check Service Status

```bash
docker-compose ps
```

## 🔍 Troubleshooting

### Issue: Services not starting

**Solution**: Check if ports are already in use:
```bash
# Check port usage
lsof -i :8501  # Streamlit
lsof -i :5000  # Web app
lsof -i :8000  # ChromaDB
lsof -i :11434 # Ollama
```

### Issue: Model download fails

**Solution**: 
1. Check your internet connection
2. Manually pull the model:
```bash
docker-compose exec ollama ollama pull llama2
```

### Issue: "No documents loaded" error

**Solution**: Load sample data or upload documents before asking questions.

### Issue: Slow response times

**Solutions**:
- Ensure you have enough RAM (16GB recommended)
- Enable GPU support if available
- Use a smaller model (edit docker-compose.yml to use `tinyllama`)

### Issue: Out of memory errors

**Solution**: 
1. Close other applications
2. Increase Docker memory limit in Docker Desktop settings
3. Use a smaller model

## 📚 Adding Your Own Documents

### Via Streamlit Interface

1. Go to http://localhost:8501
2. Use the file uploader in the sidebar
3. Supported formats: TXT, MD, PDF

### Via Web Interface

Currently, the web interface uses sample data only. To add custom documents:

1. Add your text files to the `data/` directory
2. Restart the services:
```bash
docker-compose restart web-app
```

### Via API (Web App)

```bash
# The documents in data/ directory are automatically available
# Just click "Load Sample Data" button
```

## 🎯 Use Cases

- **Documentation Q&A**: Load your documentation and ask questions
- **Research Assistant**: Query your research papers
- **Knowledge Base**: Create a searchable knowledge base
- **Customer Support**: Build a support bot with your FAQs
- **Education**: Create interactive learning materials

## 🔐 Security Notes

- This application is designed for local use
- No data is sent to external services
- All processing happens on your machine
- For production deployment, add authentication and HTTPS

## 🚀 Advanced Usage

### Using Different Models

Edit `docker-compose.yml` and change the model in `ollama-init` service:

```yaml
command:
  - |
    echo "Pulling mistral model..."
    ollama pull mistral --base-url http://ollama:11434
```

Available models:
- `llama2` (default, 7B parameters)
- `mistral` (7B parameters)
- `codellama` (7B parameters, optimized for code)
- `tinyllama` (1.1B parameters, faster but less accurate)

### Customizing Chunk Size

Edit `streamlit-app/utils/document_loader.py` or `web-app/server.py`:

```python
chunk_size = 1000  # Change to your preferred size
chunk_overlap = 200  # Overlap between chunks
```

### Changing the Number of Retrieved Documents

Edit `streamlit-app/utils/rag_chain.py` or `web-app/server.py`:

```python
n_results = 3  # Change to retrieve more/fewer documents
```

## 📈 Performance Tips

1. **Use GPU**: Enables significantly faster inference
2. **Adjust Chunk Size**: Smaller chunks = more precise, larger chunks = more context
3. **Tune n_results**: More results = more context but slower
4. **Use Smaller Models**: For faster responses with less accuracy
5. **Increase RAM**: Allows for larger models and more documents

## 🤝 Contributing

This is a complete, ready-to-use RAG system. Feel free to:
- Add new features
- Improve the UI
- Add support for more document types
- Implement authentication
- Add more AI models

## 📝 License

This project is provided as-is for educational and commercial use.

## 🙏 Acknowledgments

- **Ollama**: For providing easy-to-use local LLM inference
- **ChromaDB**: For the excellent vector database
- **Streamlit**: For the rapid UI development framework
- **LangChain**: For RAG implementation patterns

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs: `docker-compose logs`
3. Ensure all prerequisites are met
4. Try restarting: `docker-compose restart`

## 🎓 Learning Resources

- [Ollama Documentation](https://ollama.ai/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [RAG Concepts](https://www.anthropic.com/research/rag)

---

**Happy RAG-ing! 🚀**
