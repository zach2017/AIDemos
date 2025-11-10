# 🔧 Troubleshooting Guide

Common issues and their solutions for the Apache Iceberg + RAG Demo.

---

## 🚨 Docker Compose Issues

### Error: "path not found" when running docker-compose up

**Full Error:**
```
unable to prepare context: path "C:\Users\...\app" not found
```

**Cause:** Directory structure issue or missing files

**Solution:**

**Option 1: Verify Directory Structure**
```bash
# Make sure you're in the correct directory
cd iceberg-demo

# Check if app directory exists
ls -la
# You should see: app/, scripts/, docker/, etc.

# If app/ is missing, create it:
mkdir -p app
```

**Option 2: Extract Zip Properly**
```bash
# Make sure to extract the ENTIRE zip file
# Not just individual files

# On Windows:
# Right-click → Extract All → Select destination

# On Mac/Linux:
unzip iceberg-demo.zip
cd iceberg-demo
```

**Option 3: Use Updated docker-compose.yml**

The latest version doesn't require building, it uses volume mounts:
```yaml
webapp:
  image: python:3.11-slim
  volumes:
    - ./app:/app
```

**Option 4: Skip Web App for Now**

Comment out the webapp service in docker-compose.yml:
```yaml
# webapp:
#   image: python:3.11-slim
#   ...
```

Then start without webapp:
```bash
docker-compose up -d
```

---

### Error: Port already in use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8501: bind: address already in use
```

**Solution:**

**Option 1: Stop the conflicting service**
```bash
# Find what's using the port
# On Windows:
netstat -ano | findstr :8501

# On Mac/Linux:
lsof -i :8501

# Stop the process using that port
```

**Option 2: Change the port**

Edit `docker-compose.yml`:
```yaml
webapp:
  ports:
    - "8502:8501"  # Changed from 8501 to 8502
```

Then access at: http://localhost:8502

---

### Error: Cannot connect to Docker daemon

**Error:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solution:**

**Make sure Docker Desktop is running**
- Windows: Start Docker Desktop from Start Menu
- Mac: Start Docker Desktop from Applications
- Linux: `sudo systemctl start docker`

**Check Docker status:**
```bash
docker ps
# Should show running containers, not an error
```

---

## 🗄️ Service Connection Issues

### Chroma shows "Disconnected" in web app

**Symptom:** Red ❌ next to "Chroma" in sidebar

**Solution:**

**Check if Chroma is running:**
```bash
docker-compose ps
# Look for "chroma" service - should say "running"
```

**Restart Chroma:**
```bash
docker-compose restart chroma

# Wait 10 seconds, then refresh browser
```

**Check logs:**
```bash
docker-compose logs chroma
# Look for any error messages
```

---

### Ollama shows "Disconnected" in web app

**Symptom:** Red ❌ next to "Ollama" in sidebar

**Solution:**

**Check if Ollama is running:**
```bash
docker-compose ps
# Look for "ollama" service
```

**Restart Ollama:**
```bash
docker-compose restart ollama

# Wait 30 seconds (Ollama takes time to start)
```

**Pull models manually:**
```bash
docker exec -it ollama ollama pull nomic-embed-text
docker exec -it ollama ollama pull llama3.2:1b
```

---

### "No products found" in web app

**Symptom:** Product catalog is empty

**Cause:** Demo hasn't been run yet to populate data

**Solution:**

**Run the demo to initialize data:**
```bash
docker exec -it iceberg-app python /app/scripts/demo.py
```

This will:
- Create Iceberg tables
- Load sample products
- Generate embeddings
- Store in Chroma

**Wait 5-10 minutes** for first run (downloads models)

**Refresh browser** after demo completes

---

## 🌐 Web App Issues

### Web app not loading (blank page)

**Solution:**

**Check if webapp container is running:**
```bash
docker-compose ps webapp
# Should show "running" status
```

**View webapp logs:**
```bash
docker-compose logs -f webapp
# Look for "You can now view your Streamlit app"
```

**Restart webapp:**
```bash
docker-compose restart webapp
# Wait 30 seconds for dependencies to install
```

**Access directly:**
```bash
# Try: http://localhost:8501
# Also try: http://127.0.0.1:8501
```

---

### Web app loads but shows errors

**Solution:**

**Check all services are healthy:**
```bash
make health
# OR
docker exec -it iceberg-app python /app/scripts/health_check.py
```

**Restart all services:**
```bash
docker-compose restart
```

**Clean restart:**
```bash
docker-compose down
docker-compose up -d
```

---

### Slow response times in web app

**Symptom:** Queries take 30+ seconds

**Cause:** First query after startup is always slow (model loading)

**Solution:**

**Normal behavior:**
- First query: 20-30 seconds (loading models)
- Subsequent queries: 2-5 seconds

**If always slow:**

**Check system resources:**
```bash
# Docker Desktop → Settings → Resources
# Ensure: 8GB RAM, 4 CPUs allocated
```

**Reduce number of results:**
- In Smart Search tab, set slider to 3 instead of 10

**Close other applications:**
- Free up RAM and CPU

---

## 💻 Python Script Issues

### ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'chromadb'
```

**Solution:**

**You're running scripts outside Docker:**

**Option 1: Use Docker (Recommended)**
```bash
# Always run scripts through Docker:
docker exec -it iceberg-app python /app/scripts/demo.py
```

**Option 2: Install locally**
```bash
pip install --break-system-packages \
  pyspark==3.5.0 \
  pyiceberg[s3fs,pyarrow]==0.6.1 \
  chromadb==0.4.18 \
  ollama==0.1.7 \
  boto3==1.34.27 \
  pandas==2.1.4
```

---

### Demo script hangs during model download

**Symptom:** Stuck at "Pulling nomic-embed-text model..."

**Cause:** Large model download (~2GB), slow internet

**Solution:**

**Be patient:**
- First download takes 5-10 minutes
- No progress bar shown
- Check Docker logs:
  ```bash
  docker-compose logs -f ollama
  ```

**Download models separately:**
```bash
docker exec -it ollama ollama pull nomic-embed-text
docker exec -it ollama ollama pull llama3.2:1b
```

---

## 📊 Data Issues

### Cannot query Iceberg tables

**Error:**
```
Table not found: demo.products_db.products
```

**Solution:**

**Run the demo first:**
```bash
docker exec -it iceberg-app python /app/scripts/demo.py
```

**Check table exists:**
```bash
docker exec -it spark-iceberg spark-sql

# Then in spark-sql:
SHOW DATABASES;
USE demo.products_db;
SHOW TABLES;
```

---

### LocalStack S3 errors

**Error:**
```
Could not connect to the endpoint URL
```

**Solution:**

**Check LocalStack is running:**
```bash
docker-compose ps localstack
```

**Check LocalStack health:**
```bash
curl http://localhost:4566/_localstack/health
```

**Restart LocalStack:**
```bash
docker-compose restart localstack
```

---

## 🧹 Reset Everything

### Complete Clean Slate

**When nothing else works:**

```bash
# 1. Stop all services
docker-compose down

# 2. Remove all volumes (WARNING: deletes all data)
docker-compose down -v

# 3. Remove data directories
rm -rf chroma-data/ ollama-data/ localstack-data/

# 4. Start fresh
docker-compose up -d

# 5. Wait for services to start (2-3 minutes)
docker-compose logs -f

# 6. Run demo
docker exec -it iceberg-app python /app/scripts/demo.py

# 7. Open web app
make webapp
```

---

## 🐞 Debug Mode

### Enable Verbose Logging

**For Python scripts:**
```python
# Add to top of any script:
import logging
logging.basicConfig(level=logging.DEBUG)
```

**For Docker Compose:**
```bash
# View all logs:
docker-compose logs -f

# View specific service:
docker-compose logs -f webapp
docker-compose logs -f chroma
docker-compose logs -f ollama
```

**For Spark:**
```python
# In demo.py, change:
spark.sparkContext.setLogLevel("DEBUG")  # Instead of "WARN"
```

---

## 💾 System Requirements Check

### Minimum Requirements

**Check Docker resources:**

1. Open Docker Desktop
2. Go to Settings → Resources
3. Verify:
   - Memory: **8 GB minimum** (12 GB recommended)
   - CPUs: **4 cores minimum**
   - Disk: **10 GB free**

**Check disk space:**
```bash
# Check available space:
df -h

# Docker uses:
# - Ollama models: ~2 GB
# - Container images: ~3 GB
# - Data: ~1 GB
# Total: ~6 GB + your data
```

---

## 🔍 Common Workflow Issues

### Issue: "Make command not found"

**Solution:**

**On Windows:**
```bash
# Install make via Chocolatey:
choco install make

# Or use commands directly:
docker-compose up -d
docker exec -it iceberg-app python /app/scripts/demo.py
```

**On Mac:**
```bash
# Install via Homebrew:
brew install make
```

---

### Issue: File permissions (Linux only)

**Error:**
```
Permission denied
```

**Solution:**
```bash
# Fix ownership:
sudo chown -R $USER:$USER .

# Or run with sudo:
sudo docker-compose up -d
```

---

## 📞 Still Having Issues?

### Diagnostic Information to Collect

Run these commands and share output:

```bash
# 1. Docker version
docker --version
docker-compose --version

# 2. Services status
docker-compose ps

# 3. Logs
docker-compose logs --tail=50

# 4. System info
docker info | grep -E "CPU|Memory"

# 5. Directory structure
ls -la
```

### Where to Get Help

1. **Check Documentation:**
   - README.md - Full reference
   - WEBAPP_GUIDE.md - Web app help
   - TUTORIAL.md - Learning guide

2. **Check Logs:**
   - Always check logs first
   - `docker-compose logs -f`

3. **GitHub Issues:**
   - Search for similar issues
   - Create new issue with diagnostic info

---

## ✅ Quick Checklist

Before reporting issues, verify:

- [ ] Docker Desktop is running
- [ ] You're in the `iceberg-demo/` directory
- [ ] All files extracted properly from zip
- [ ] Docker has 8GB+ RAM allocated
- [ ] No port conflicts (8501, 8000, 11434, 4566)
- [ ] Demo script was run successfully
- [ ] Services show "running" in `docker-compose ps`
- [ ] You waited 2-3 minutes after starting services

---

## 🎯 Pro Tips

### Make Life Easier

**Use health check:**
```bash
# Always run this first when troubleshooting:
make health
```

**Watch logs in real-time:**
```bash
# Open in separate terminal:
docker-compose logs -f
```

**Restart individual services:**
```bash
# Instead of restarting everything:
docker-compose restart webapp
docker-compose restart chroma
```

**Use make commands:**
```bash
make help    # See all commands
make health  # Check status
make demo    # Run demo
make logs    # View logs
```

---

**Most issues can be solved by:**
1. Checking if services are running
2. Running the demo script
3. Restarting the problematic service
4. Reading the logs

Good luck! 🚀
