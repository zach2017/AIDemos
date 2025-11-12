# Docker Compose Setup Guide

Complete guide for running the Document Embeddings & Query System with Docker and Ollama.

## Quick Start with Docker Compose

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)
- At least 4GB free RAM
- At least 5GB free disk space

### 1. Start the Services

```bash
# Start all services (Flask app + Ollama)
docker-compose up -d

# View logs
docker-compose logs -f
```

The application will be available at:
- **Web Interface**: http://localhost:5000
- **Ollama API**: http://localhost:11434

### 2. Pull an Ollama Model

Once the services are running, you need to pull at least one LLM model:

```bash
# Pull a small, fast model (recommended for testing)
docker exec -it ollama_service ollama pull llama2

# Or pull other models:
docker exec -it ollama_service ollama pull mistral
docker exec -it ollama_service ollama pull phi
docker exec -it ollama_service ollama pull neural-chat

# List installed models
docker exec -it ollama_service ollama list
```

### 3. Use the Application

1. Open http://localhost:5000 in your browser
2. **Ingest Documents**:
   - Click "Ingest Documents" tab
   - Upload your text files
   - Configure settings (or use defaults)
   - Click "Build Embeddings"

3. **Query Documents**:
   - Click "Query Database" tab
   - Enter your question
   - (Optional) Check "Use Ollama for RAG" and enter model name
   - Click "Search"

### 4. Stop the Services

```bash
# Stop services
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v
```

## Available Ollama Models

### Small Models (Good for Testing)
- **phi** (~2.7GB) - Fast, good for simple queries
- **neural-chat** (~4.1GB) - Optimized for chat

### Medium Models (Balanced)
- **llama2** (~3.8GB) - Meta's Llama 2 model
- **mistral** (~4.1GB) - High-quality open model

### Large Models (Best Quality)
- **llama2:13b** (~7.3GB) - Larger Llama 2 variant
- **llama2:70b** (~39GB) - Highest quality (requires lots of RAM)

## Configuration

### Environment Variables

You can customize the application by editing `docker-compose.yml`:

```yaml
environment:
  - FLASK_ENV=development  # or 'production'
  - OLLAMA_HOST=http://ollama:11434
```

### GPU Support (NVIDIA Only)

To enable GPU acceleration for Ollama:

1. Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

2. Uncomment GPU section in `docker-compose.yml`:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

3. Restart services:
```bash
docker-compose down
docker-compose up -d
```

### Persistent Storage

Data is stored in Docker volumes and local directories:
- **Vector Database**: `./chroma_db` (persisted locally)
- **Uploaded Files**: `./uploads` (temporary)
- **Ollama Models**: `ollama_data` volume

## Troubleshooting

### Service Won't Start

```bash
# Check service status
docker-compose ps

# View detailed logs
docker-compose logs web
docker-compose logs ollama
```

### Out of Memory

If you're running out of memory:
1. Use smaller models (phi, mistral)
2. Increase Docker Desktop memory limit
3. Close other applications

### Ollama Connection Error

```bash
# Test Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
docker-compose restart ollama
```

### Port Already in Use

If port 5000 or 11434 is already in use, edit `docker-compose.yml`:

```yaml
ports:
  - "5001:5000"  # Change external port to 5001
```

## Advanced Usage

### Running Without Ollama

If you only want semantic search without RAG:

```bash
# Run only the web service
docker-compose up -d web
```

### Custom Ollama Models

```bash
# Pull specific model version
docker exec -it ollama_service ollama pull llama2:13b

# Create custom modelfile
docker exec -it ollama_service ollama create mymodel -f Modelfile
```

### Backup Your Data

```bash
# Backup vector database
tar -czf chroma_backup.tar.gz chroma_db/

# Backup Ollama models
docker run --rm -v ollama_data:/data -v $(pwd):/backup \
  busybox tar -czf /backup/ollama_backup.tar.gz /data
```

## Performance Tips

1. **Use SSD Storage**: Place `chroma_db` on SSD for faster queries
2. **Chunk Size**: Larger chunks (1000-1500) work better with LLMs
3. **Top K**: Start with k=4, increase for more context
4. **Model Selection**: 
   - Simple queries: phi, neural-chat
   - Complex queries: llama2, mistral
   - Maximum quality: llama2:13b or llama2:70b

## API Endpoints

The Flask application exposes these endpoints:

- `GET /` - Web interface
- `POST /upload` - Upload and ingest documents
- `POST /query` - Query the database
- `GET /ollama/models` - List available Ollama models
- `GET /health` - Health check

## Security Notes

⚠️ This setup is for local development. For production:

1. Change the Flask secret key in `app.py`
2. Set `FLASK_ENV=production`
3. Use a reverse proxy (nginx)
4. Enable HTTPS
5. Add authentication
6. Restrict CORS

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Docker Documentation](https://docs.docker.com/)
