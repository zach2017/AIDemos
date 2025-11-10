# 🚀 Initialization Guide

## Complete Setup Steps in Correct Order

This guide shows you the **exact steps** to get everything working, especially for the first run.

---

## ⚡ Quick Start (Copy-Paste)

```bash
# Step 1: Navigate to directory
cd iceberg-demo

# Step 2: Start all services
docker-compose up -d

# Step 3: Wait for services (2-3 minutes)
# Watch logs (optional):
docker-compose logs -f

# Press Ctrl+C when you see services starting

# Step 4: Initialize data (REQUIRED - takes 5-10 minutes first time)
docker exec -it iceberg-app python /app/scripts/demo.py

# Step 5: Open web app
# Visit: http://localhost:8501
# Or run: make webapp
```

---

## 📋 Detailed Step-by-Step

### Step 1: Extract and Navigate

```bash
# Windows:
cd C:\Users\YourName\iceberg-demo

# Mac/Linux:
cd ~/iceberg-demo
```

**Verify files exist:**
```bash
# Windows:
dir

# Mac/Linux:
ls -la
```

**You should see:**
- app/
- scripts/
- docker/
- docker-compose.yml
- Makefile
- README.md and other .md files

---

### Step 2: Start Docker Services

```bash
docker-compose up -d
```

**What happens:**
- Downloads Docker images (~3 GB first time)
- Starts 6 containers
- Creates data directories

**Wait 2-3 minutes** for all services to start.

**Check status:**
```bash
docker-compose ps
```

**Expected output:**
```
NAME                STATUS
localstack          running
spark-iceberg       running
chroma              running
ollama              running
iceberg-app         running
iceberg-webapp      running (healthy)
```

**If any show "starting":** Wait another minute and check again.

---

### Step 3: Verify Services are Ready

```bash
docker exec -it iceberg-app python /app/scripts/health_check.py
```

**Expected output:**
```
✅ LocalStack S3: Running
✅ Chroma Vector DB: Running
✅ Ollama: Running (0 models loaded)  ← This is OK for now

Additional Checks:
⚠️ S3 Bucket 'iceberg-warehouse': Not found (run demo.py to create)
⚠️ Chroma Collection 'products': Not found (run demo.py to create)
```

**This is NORMAL before running the demo!**

---

### Step 4: Initialize Data (IMPORTANT!)

This step is **required** before using the web app or CLI queries.

```bash
docker exec -it iceberg-app python /app/scripts/demo.py
```

**What this does:**
1. Creates S3 bucket in LocalStack
2. Initializes Spark with Iceberg
3. Creates products database and table
4. Loads 6 sample products
5. Downloads Ollama models (~2 GB)
   - nomic-embed-text (embeddings)
   - llama3.2:1b (text generation)
6. Generates embeddings for all products
7. Stores embeddings in Chroma
8. Runs sample queries

**Time required:**
- **First run:** 5-10 minutes (downloads models)
- **Subsequent runs:** 2-3 minutes

**What you'll see:**
```
=== Setting up S3 Bucket ===
✓ Created S3 bucket: iceberg-warehouse

=== Creating Spark Session ===
✓ Spark session created

=== Creating Iceberg Table ===
✓ Created database: demo.products_db
✓ Created and populated Iceberg table
✓ Table contains 6 records

=== Setting up Ollama Model ===
Pulling nomic-embed-text model (this may take a few minutes)...
.................................................
✓ Model nomic-embed-text is ready

Pulling llama3.2:1b model for Q&A...
.................................................
✓ Model llama3.2:1b is ready

=== Setting up Chroma Vector Database ===
✓ Created Chroma collection: products
Generating embeddings and storing in Chroma...
  ✓ Added Laptop Pro 15
  ✓ Added Wireless Mouse
  ✓ Added Standing Desk
  ✓ Added Mechanical Keyboard
  ✓ Added Office Chair
  ✓ Added USB-C Hub

✓ Stored 6 products in Chroma with embeddings

=== Running Sample Queries ===
[Sample queries and results shown...]

✅ All Advanced Demos Complete!
```

**If it gets stuck:**
- Be patient during model downloads (no progress bar)
- Check logs: `docker-compose logs -f ollama`
- First download is large (~2 GB)

---

### Step 5: Verify Initialization

```bash
docker exec -it iceberg-app python /app/scripts/health_check.py
```

**Expected output NOW:**
```
✅ LocalStack S3: Running
✅ Chroma Vector DB: Running
✅ Ollama: Running (2 models loaded)  ← Changed!

Additional Checks:
✅ S3 Bucket 'iceberg-warehouse': Created  ← Changed!
✅ Chroma Collection 'products': 6 documents  ← Changed!

✅ All core services are healthy!

Next steps:
  1. Run demo: docker exec -it iceberg-app python /app/scripts/demo.py ← Already done!
  2. Query: docker exec -it iceberg-app python /app/scripts/query.py
```

---

### Step 6: Use the System

#### Option A: Web Interface (Recommended)

```bash
# Open in browser:
make webapp

# Or visit directly:
# http://localhost:8501
```

**You should see:**
- ✅ Green status in sidebar (Chroma Connected, Ollama Connected)
- ✅ "Collections: 1" and "Models Loaded: 2"
- ✅ All 4 tabs accessible
- ✅ Product catalog showing 6 products

**If you see errors:**
- Refresh the page (F5)
- Check services: `docker-compose ps`
- Re-run demo if needed

#### Option B: Command Line Interface

```bash
# Interactive mode:
docker exec -it iceberg-app python /app/scripts/query.py

# Direct question:
docker exec -it iceberg-app python /app/scripts/query.py "What laptops do you have?"
```

---

## 🔍 Common Issues

### Issue 1: Web app shows "System Not Initialized"

**Cause:** Demo wasn't run yet

**Solution:**
```bash
docker exec -it iceberg-app python /app/scripts/demo.py
```

Then refresh browser (F5).

---

### Issue 2: "No products found" in web app

**Cause:** Chroma collection is empty

**Solution:**
```bash
# Re-run initialization:
docker exec -it iceberg-app python /app/scripts/demo.py
```

---

### Issue 3: Demo hangs during model download

**Cause:** Large model download, slow internet

**Solution:**
- **Be patient** - first download takes time
- Check progress: `docker-compose logs -f ollama`
- Download manually:
  ```bash
  docker exec -it ollama ollama pull nomic-embed-text
  docker exec -it ollama ollama pull llama3.2:1b
  ```

---

### Issue 4: Services not starting

**Solution:**
```bash
# Check status:
docker-compose ps

# View logs:
docker-compose logs -f

# Restart specific service:
docker-compose restart [service-name]

# Restart all:
docker-compose restart
```

---

### Issue 5: Out of disk space

**Cause:** Ollama models are large (~2 GB)

**Solution:**
```bash
# Check disk space:
df -h

# Clean Docker if needed:
docker system prune -a

# Ensure 10 GB free before starting
```

---

## 🎯 Initialization Checklist

Before considering initialization complete:

- [ ] All 6 containers running (`docker-compose ps`)
- [ ] Health check shows all green (`make health`)
- [ ] S3 bucket created
- [ ] Chroma collection with 6 documents
- [ ] 2 Ollama models loaded
- [ ] Web app loads without errors
- [ ] Web app sidebar shows green status
- [ ] Product catalog shows 6 items
- [ ] Smart Search returns results

---

## ⏱️ Time Expectations

### First Time Setup
- Extract zip: 10 seconds
- `docker-compose up -d`: 5-10 minutes (image download)
- Services starting: 2-3 minutes
- `demo.py` first run: 5-10 minutes (model download)
- **Total: ~20-25 minutes**

### Subsequent Startups
- `docker-compose up -d`: 10 seconds
- Services starting: 1-2 minutes
- `demo.py` (if re-run): 2-3 minutes
- **Total: ~3-5 minutes**

---

## 🔄 Resetting Everything

If you need to start fresh:

```bash
# Stop services:
docker-compose down

# Remove all data (WARNING: deletes everything):
docker-compose down -v
rm -rf chroma-data/ ollama-data/ localstack-data/

# Start fresh:
docker-compose up -d
docker exec -it iceberg-app python /app/scripts/demo.py
```

---

## 📊 What Gets Created

### During `docker-compose up -d`:
```
Creates on disk:
├── chroma-data/          # Empty initially
├── ollama-data/          # Empty initially
├── localstack-data/      # Empty initially
└── Docker volumes        # Container data
```

### During `demo.py`:
```
Populates:
├── chroma-data/
│   └── products collection (6 items, 768-dim vectors each)
├── ollama-data/
│   ├── nomic-embed-text model (~274 MB)
│   └── llama3.2:1b model (~1.3 GB)
└── localstack-data/
    └── iceberg-warehouse/
        └── warehouse/
            └── products_db/
                └── products/ (Parquet files + metadata)
```

---

## 🎓 Understanding the Flow

```
User starts services
        ↓
Docker Compose
├─ Pulls images
├─ Creates networks
├─ Starts containers
└─ Waits for health checks
        ↓
Services ready (empty)
        ↓
User runs demo.py
├─ Connects to services
├─ Creates S3 bucket
├─ Creates Iceberg tables
├─ Loads sample data
├─ Downloads Ollama models
├─ Generates embeddings
└─ Stores in Chroma
        ↓
System initialized
        ↓
User opens web app
└─ Reads from Chroma ✅
        ↓
Asks questions
└─ Searches vectors, gets AI answers ✅
```

---

## 💡 Pro Tips

### Tip 1: Watch Logs During First Run
```bash
# In separate terminal:
docker-compose logs -f

# This shows real-time progress
```

### Tip 2: Pre-download Models
```bash
# Before running demo, manually pull models:
docker exec -it ollama ollama pull nomic-embed-text
docker exec -it ollama ollama pull llama3.2:1b

# Then demo.py will skip downloads
```

### Tip 3: Use Make Commands
```bash
make up      # = docker-compose up -d
make demo    # = docker exec -it iceberg-app python /app/scripts/demo.py
make health  # = docker exec -it iceberg-app python /app/scripts/health_check.py
make webapp  # Opens browser
make help    # Shows all commands
```

### Tip 4: Keep Services Running
```bash
# Don't run docker-compose down unless needed
# Just keep services running and use them

# When done for the day:
docker-compose stop     # Stops but keeps data

# Next day:
docker-compose start    # Resumes
```

---

## ✅ Success Indicators

You know initialization worked when:

1. **Health check output:**
   ```
   ✅ All core services are healthy!
   ✅ S3 Bucket 'iceberg-warehouse': Created
   ✅ Chroma Collection 'products': 6 documents
   ```

2. **Web app sidebar:**
   ```
   ✅ Chroma Connected
   📊 Collections: 1
   
   ✅ Ollama Connected
   📊 Models Loaded: 2
   ```

3. **Smart Search works:**
   - Type question
   - Get products
   - See AI answer

4. **Product Catalog:**
   - Shows 6 products
   - Can filter and sort
   - Statistics display

---

## 🆘 Still Having Issues?

1. **Read:** TROUBLESHOOTING.md
2. **Check:** QUICK_FIX.md
3. **Review:** docker-compose logs
4. **Verify:** Directory structure (DIRECTORY_STRUCTURE.md)
5. **Reset:** Follow "Resetting Everything" section above

---

**Follow these steps exactly and everything will work! 🎉**

The key is running `demo.py` **after** services start but **before** using the web app.
