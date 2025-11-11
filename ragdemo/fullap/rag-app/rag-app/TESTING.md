# Testing Guide

This guide helps you test the RAG application to ensure everything is working correctly.

## Pre-Testing Checklist

Before running tests, ensure:

- [ ] Docker is installed and running
- [ ] Docker Compose is available
- [ ] At least 8GB RAM allocated to Docker
- [ ] Ports 5000, 8501, 8000, and 11434 are available
- [ ] Internet connection (for first-time model download)

## Testing Steps

### 1. Start the Application

```bash
./start.sh
# or
docker-compose up -d
```

**Expected Output:**
- All 5 services should start
- Status: healthy for ollama and chromadb
- No errors in logs

### 2. Verify Services Are Running

```bash
docker-compose ps
```

**Expected Output:**
```
NAME                  STATUS
rag-chromadb          Up (healthy)
rag-ollama            Up (healthy)
rag-ollama-init       Exited (0)
rag-streamlit         Up
rag-webapp            Up
```

### 3. Check Model Download (First Time Only)

```bash
docker-compose logs -f ollama-init
```

**Expected Output:**
- Should show "Pulling llama2 model..."
- Progress indicators
- "Model ready!" at the end

### 4. Test Ollama Directly

```bash
curl http://localhost:11434/api/tags
```

**Expected Output:**
```json
{
  "models": [
    {
      "name": "llama2:latest",
      ...
    }
  ]
}
```

### 5. Test ChromaDB

```bash
curl http://localhost:8000/api/v1/heartbeat
```

**Expected Output:**
```json
{
  "nanosecond heartbeat": <timestamp>
}
```

### 6. Test Streamlit Interface

#### Manual Test:
1. Open http://localhost:8501
2. You should see the RAG Q&A System interface
3. Click "📖 Load Sample Data" in sidebar
4. Wait for success message
5. Type a question: "What is Python?"
6. Click send or press Enter
7. You should receive an AI-generated answer

**Expected Behavior:**
- Interface loads without errors
- Sample data loads successfully
- Questions get answered within 10-30 seconds
- Sources are displayed below answers

### 7. Test Web Interface

#### Manual Test:
1. Open http://localhost:5000
2. You should see the web interface
3. Click "📖 Load Sample Data"
4. Wait for success message
5. Type a question: "What is machine learning?"
6. Click "Send"
7. You should receive an answer

**Expected Behavior:**
- Clean, responsive interface
- Data loads without errors
- Questions are answered correctly
- Sources shown in expandable sections

### 8. Test API Endpoints (Web App)

#### Health Check:
```bash
curl http://localhost:5000/api/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "ollama_url": "http://ollama:11434",
  "chroma_host": "chromadb",
  "chroma_port": 8000
}
```

#### Load Sample Data:
```bash
curl -X POST http://localhost:5000/api/load-sample-data
```

**Expected Output:**
```json
{
  "success": true,
  "message": "Loaded X document chunks",
  "count": X
}
```

#### Query:
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Docker?"}'
```

**Expected Output:**
```json
{
  "success": true,
  "answer": "Docker is a platform...",
  "sources": ["...", "..."]
}
```

#### Status:
```bash
curl http://localhost:5000/api/status
```

**Expected Output:**
```json
{
  "success": true,
  "document_count": X,
  "collection_ready": true
}
```

## Test Scenarios

### Scenario 1: Basic Q&A
1. Load sample data
2. Ask: "What is artificial intelligence?"
3. **Expected**: Answer based on AI document

### Scenario 2: Code-Related Query
1. Ask: "What are Python data types?"
2. **Expected**: Answer listing int, float, str, list, etc.

### Scenario 3: Cross-Document Query
1. Ask: "How can AI and Python be used together?"
2. **Expected**: Answer combining info from both documents

### Scenario 4: Out-of-Context Query
1. Ask: "What is the weather today?"
2. **Expected**: Response saying information is not in the knowledge base

### Scenario 5: Data Management
1. Load sample data
2. Ask a question
3. Clear vector store
4. Try asking the same question
5. **Expected**: Error message about no documents loaded

## Performance Tests

### Response Time Test
- **Acceptable**: 5-30 seconds per query
- **Good**: < 10 seconds per query
- **Excellent**: < 5 seconds per query

### Concurrent Users Test
Open multiple browser tabs and:
1. Send queries simultaneously from both interfaces
2. **Expected**: All queries should complete successfully

### Data Volume Test
1. Add multiple large documents
2. Query the system
3. **Expected**: Responses should still work, may be slower

## Common Issues and Solutions

### Issue: Services won't start
**Solution:**
```bash
docker-compose down
docker-compose up -d
```

### Issue: Model download fails
**Solution:**
```bash
docker-compose restart ollama
docker-compose restart ollama-init
docker-compose logs -f ollama-init
```

### Issue: Connection refused errors
**Solution:**
Wait 30 seconds for health checks, then:
```bash
docker-compose ps
docker-compose logs chromadb
docker-compose logs ollama
```

### Issue: Slow responses
**Solution:**
- Increase Docker RAM to 16GB
- Enable GPU support if available
- Use a smaller model (tinyllama)

### Issue: Out of memory
**Solution:**
```bash
docker-compose down
# Increase Docker memory limit
docker-compose up -d
```

## Verification Checklist

After testing, verify:

- [ ] All services are running (docker-compose ps)
- [ ] Model is downloaded (docker-compose logs ollama-init)
- [ ] Streamlit interface is accessible
- [ ] Web interface is accessible
- [ ] Sample data can be loaded
- [ ] Questions are answered correctly
- [ ] Sources are displayed
- [ ] Clear function works
- [ ] No error messages in logs
- [ ] Response times are acceptable

## Automated Test Script

Save this as `test.sh` and run with `bash test.sh`:

```bash
#!/bin/bash

echo "Starting RAG Application Tests..."
echo

# Test 1: Check Docker
echo "Test 1: Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo "✅ Docker is running"
else
    echo "❌ Docker is not running"
    exit 1
fi

# Test 2: Start services
echo
echo "Test 2: Starting services..."
docker-compose up -d
sleep 10

# Test 3: Check services
echo
echo "Test 3: Checking service status..."
docker-compose ps

# Test 4: Test Ollama
echo
echo "Test 4: Testing Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is responsive"
else
    echo "❌ Ollama is not responsive"
fi

# Test 5: Test ChromaDB
echo
echo "Test 5: Testing ChromaDB..."
if curl -s http://localhost:8000/api/v1/heartbeat > /dev/null; then
    echo "✅ ChromaDB is responsive"
else
    echo "❌ ChromaDB is not responsive"
fi

# Test 6: Test Web App
echo
echo "Test 6: Testing Web App..."
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Web App is responsive"
else
    echo "❌ Web App is not responsive"
fi

# Test 7: Test Streamlit
echo
echo "Test 7: Testing Streamlit..."
if curl -s http://localhost:8501 > /dev/null; then
    echo "✅ Streamlit is responsive"
else
    echo "❌ Streamlit is not responsive"
fi

echo
echo "Testing complete!"
echo "Open http://localhost:8501 or http://localhost:5000 to use the application"
```

## Cleanup After Testing

```bash
# Stop services
docker-compose down

# Remove all data (if needed)
docker-compose down -v

# Remove images (if needed)
docker-compose down --rmi all
```

---

## Success Criteria

Your RAG system is working correctly if:

1. ✅ All services start without errors
2. ✅ Model downloads successfully
3. ✅ Both interfaces are accessible
4. ✅ Sample data loads without issues
5. ✅ Questions are answered with relevant information
6. ✅ Sources are displayed correctly
7. ✅ Response times are acceptable (< 30 seconds)
8. ✅ System is stable after multiple queries

If all criteria are met, congratulations! Your RAG system is fully operational. 🎉
