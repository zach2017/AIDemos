# ⚡ QUICK FIX - Path Not Found Error

## Your Error:
```
unable to prepare context: path "C:\Users\zcstr\AIDemos\DemoIceberg\app" not found
```

## ✅ Solution (3 Steps)

### Step 1: Download the UPDATED zip file
The new package has a fixed `docker-compose.yml` that doesn't require building.

**Download:** iceberg-demo.zip (the latest version)

### Step 2: Extract completely
```bash
# Windows: Right-click → Extract All
# Extract to: C:\Users\zcstr\AIDemos\

# Result should be:
# C:\Users\zcstr\AIDemos\iceberg-demo\
```

### Step 3: Verify files exist
```bash
cd C:\Users\zcstr\AIDemos\iceberg-demo

# Check if app directory exists:
dir app
# Should show: Dockerfile, streamlit_app.py

# If app/ directory is missing:
mkdir app
# Then re-extract the zip file
```

### Step 4: Start services
```bash
# In: C:\Users\zcstr\AIDemos\iceberg-demo
docker-compose up -d
```

---

## 🔧 What Was Fixed

**Old version (broken):**
```yaml
webapp:
  build: ./app/  # ❌ Requires building
```

**New version (fixed):**
```yaml
webapp:
  image: python:3.11-slim  # ✅ Uses pre-built image
  volumes:
    - ./app:/app           # ✅ Mounts app directory
  command: >                # ✅ Installs deps at runtime
    bash -c "pip install ... && streamlit run ..."
```

---

## 🎯 Alternative: Skip Web App

If you still have issues, you can start without the web app:

### Option 1: Comment out webapp in docker-compose.yml

Open `docker-compose.yml` and add `#` before webapp:

```yaml
  # webapp:
  #   image: python:3.11-slim
  #   ...
```

Then start:
```bash
docker-compose up -d
```

### Option 2: Use only core services

```bash
# Start only essential services:
docker-compose up -d localstack spark-iceberg chroma ollama app

# This skips the webapp
```

You can still use the CLI:
```bash
docker exec -it iceberg-app python /app/scripts/demo.py
docker exec -it iceberg-app python /app/scripts/query.py
```

---

## 📂 Expected Directory Structure

After extracting, you should have:

```
iceberg-demo/
├── app/
│   ├── Dockerfile
│   └── streamlit_app.py    ← Must exist!
├── scripts/
│   ├── demo.py
│   ├── query.py
│   └── ...
├── docker/
│   └── app/
│       └── Dockerfile
├── docker-compose.yml       ← Fixed version
├── Makefile
├── README.md
└── ... (other .md files)
```

**If `app/` is missing:**
1. Re-extract the zip file
2. Make sure you extract the ENTIRE contents
3. Don't extract files individually

---

## ✅ Verify Fix Worked

After starting services:

```bash
# Check all containers are running:
docker-compose ps

# You should see:
# - localstack
# - spark-iceberg
# - chroma
# - ollama
# - iceberg-app
# - iceberg-webapp  ← This should be running now!

# If webapp shows as running:
# Open: http://localhost:8501
```

---

## 🆘 Still Not Working?

### Check Docker is running
```bash
docker ps
# Should NOT show an error
```

### Check you're in the right directory
```bash
# Windows:
cd C:\Users\zcstr\AIDemos\iceberg-demo
dir

# You should see: docker-compose.yml, app/, scripts/, etc.
```

### View detailed logs
```bash
docker-compose logs webapp
# Look for errors
```

### Complete reset
```bash
# Stop everything:
docker-compose down

# Re-extract zip file to fresh directory

# Start again:
docker-compose up -d
```

---

## 📞 Need More Help?

See **TROUBLESHOOTING.md** for comprehensive solutions to all common issues.

Key sections:
- Docker Compose Issues (page 1)
- Service Connection Issues (page 3)
- Web App Issues (page 5)
- Complete Clean Slate (page 8)

---

## 🎉 Success!

Once `docker-compose up -d` works without errors:

```bash
# 1. Initialize data (first time only):
docker exec -it iceberg-app python /app/scripts/demo.py

# 2. Open web app:
# Visit: http://localhost:8501

# Or use CLI:
docker exec -it iceberg-app python /app/scripts/query.py
```

---

**The updated zip file has the fix - just re-extract and try again!** ✅
