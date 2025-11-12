# Quick Reference Guide

## 🚀 Quick Start Commands

### Docker (Recommended)
```bash
# Automated setup with model installation
./setup-ollama.sh

# Or manual setup
docker-compose up -d
docker exec -it ollama_service ollama pull llama2
```

### Without Docker
```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

## 📋 Common Tasks

### Install Ollama Models
```bash
# Small & fast
docker exec -it ollama_service ollama pull phi

# Balanced quality
docker exec -it ollama_service ollama pull llama2
docker exec -it ollama_service ollama pull mistral

# High quality (large)
docker exec -it ollama_service ollama pull llama2:13b

# List installed
docker exec -it ollama_service ollama list
```

### Manage Services
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Remove everything (including data)
docker-compose down -v
```

## 🔧 Configuration Quick Reference

### Ingest Settings
| Setting | Default | Range | Purpose |
|---------|---------|-------|---------|
| Chunk Size | 800 | 100-5000 | Size of text chunks |
| Chunk Overlap | 120 | 0-500 | Overlap between chunks |
| Database Dir | ./chroma_db | path | Where to store DB |
| Collection | demo | string | Collection name |

### Query Settings
| Setting | Default | Range | Purpose |
|---------|---------|-------|---------|
| Top K | 4 | 1-20 | Results to retrieve |
| Ollama Model | - | string | LLM for RAG |
| Use RAG | false | bool | Enable AI answers |

## 📊 Model Selection Guide

### By Speed
- **Fastest**: phi (2.7GB)
- **Fast**: neural-chat (4.1GB)
- **Medium**: llama2 (3.8GB), mistral (4.1GB)
- **Slow**: llama2:13b (7.3GB)

### By Quality
- **Basic**: phi, neural-chat
- **Good**: llama2, mistral
- **Best**: llama2:13b, llama2:70b

### By Use Case
- **Simple Q&A**: phi
- **General purpose**: llama2, mistral
- **Complex reasoning**: llama2:13b
- **Production**: mistral (good quality/speed)

## 🌐 API Endpoints

### Ingest
```bash
curl -X POST http://localhost:5000/upload \
  -F "files[]=@document.txt" \
  -F "collection_name=my_docs" \
  -F "chunk_size=800"
```

### Query (No RAG)
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this about?",
    "collection_name": "my_docs",
    "k": 4,
    "use_ollama": false
  }'
```

### Query (With RAG)
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize the main points",
    "collection_name": "my_docs",
    "k": 4,
    "use_ollama": true,
    "ollama_model": "llama2"
  }'
```

### List Models
```bash
curl http://localhost:5000/ollama/models
```

## 🐛 Troubleshooting

### Ollama Not Connecting
```bash
# Check if running
docker ps | grep ollama

# Test connection
curl http://localhost:11434/api/tags

# Restart service
docker-compose restart ollama
```

### Port Already in Use
```bash
# Change port in docker-compose.yml
ports:
  - "5001:5000"  # Use 5001 instead
```

### Out of Memory
```bash
# Use smaller model
docker exec -it ollama_service ollama pull phi

# Increase Docker memory (Docker Desktop → Settings → Resources)
```

### Database Not Found
```bash
# Make sure you've ingested documents first
# Check database path matches between ingest and query
```

## 📁 File Structure
```
project/
├── app.py                    # Flask application
├── templates/
│   └── index.html           # Web interface
├── static/
│   └── app.js              # JavaScript
├── docker-compose.yml       # Docker setup
├── Dockerfile              # Flask container
├── requirements.txt        # Python deps
├── README.md              # Full docs
├── DOCKER_GUIDE.md       # Docker docs
├── setup-ollama.sh       # Quick setup
├── example_api_usage.py  # API examples
└── chroma_db/           # Database (created)
```

## 🎯 Best Practices

### Chunk Size Selection
- **Small docs** (tweets, Q&A): 400-600
- **Medium docs** (articles, blogs): 800-1200
- **Large docs** (papers, books): 1200-1500

### Top-K Selection
- **Precise questions**: k=2-3
- **General questions**: k=4-6
- **Complex questions**: k=8-12

### Model Selection
- **Development**: phi (fastest)
- **Testing**: mistral (good balance)
- **Production**: llama2:13b (best quality)

## 🔗 Useful Links
- Web UI: http://localhost:5000
- Ollama API: http://localhost:11434
- Ollama Models: https://ollama.ai/library
- Docker Hub: https://hub.docker.com/r/ollama/ollama
