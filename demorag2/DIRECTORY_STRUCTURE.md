# 📁 Directory Structure

## Complete Package Structure

```
iceberg-demo/
│
├── 📚 Documentation (14 files, 120+ pages)
│   ├── START_HERE.md ⭐              # Start here! Navigation guide
│   ├── QUICK_FIX.md ⚡               # Fix "path not found" error
│   ├── QUICKSTART.md 🚀             # 5-minute setup guide
│   ├── README.md 📖                 # Complete reference manual
│   ├── TUTORIAL.md 🎓               # RAG + Big Data tutorial (30 pages)
│   ├── CHEATSHEET.md ⚡             # Quick reference card
│   ├── TROUBLESHOOTING.md 🔧        # All common issues (20 pages)
│   ├── WEBAPP_GUIDE.md 🌐           # Web app user guide (15 pages)
│   ├── WEBAPP_VISUAL_GUIDE.md 📸    # Visual walkthrough (20 pages)
│   ├── WHATS_NEW.md 🆕              # What was added
│   ├── ARCHITECTURE.md 🏗️           # System architecture
│   ├── PROJECT_SUMMARY.md 📊        # Overview & use cases
│   └── .gitignore                   # Git ignore rules
│
├── 🌐 Web Application
│   └── app/
│       ├── streamlit_app.py         # Main web interface (600+ lines)
│       └── Dockerfile               # Streamlit container config
│
├── 🐍 Python Scripts
│   └── scripts/
│       ├── demo.py                  # Main demo initialization ⭐
│       ├── query.py                 # Interactive CLI queries
│       ├── health_check.py          # System status check
│       ├── advanced_features.py     # Time travel & schema evolution
│       └── ingest_data.py           # Add new products
│
├── 🐳 Docker Configuration
│   ├── docker-compose.yml           # All services configuration ⭐
│   ├── Makefile                     # Convenient commands
│   └── docker/
│       └── app/
│           └── Dockerfile           # Python app container
│
└── 📂 Data Directories (created at runtime)
    ├── chroma-data/                 # Chroma vector database storage
    ├── ollama-data/                 # Ollama models (~2GB)
    ├── localstack-data/             # LocalStack S3 data
    ├── data/                        # Shared data directory
    └── notebooks/                   # Jupyter notebooks (optional)
```

## File Sizes

| File | Size | Purpose |
|------|------|---------|
| `app/streamlit_app.py` | 25 KB | Web application |
| `scripts/demo.py` | 14 KB | Initialization |
| `TUTORIAL.md` | 31 KB | Learning guide |
| `TROUBLESHOOTING.md` | 15 KB | Problem solving |
| `WEBAPP_VISUAL_GUIDE.md` | 24 KB | UI guide |
| **Total Package** | **~71 KB** | Everything |

## Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| LocalStack | 4566 | S3 API |
| Spark UI | 8080 | Monitoring |
| Jupyter | 8888 | Notebooks |
| Chroma | 8000 | Vector DB |
| **Web App** | **8501** | **Main UI** 🌐 |
| Ollama | 11434 | LLM API |

## Important Files

### Must Read First
1. **START_HERE.md** - Navigation and overview
2. **QUICK_FIX.md** - If you have errors
3. **QUICKSTART.md** - Get started in 5 minutes

### For Learning
4. **TUTORIAL.md** - Complete explanation of how it works
5. **CHEATSHEET.md** - Quick concepts reference

### For Using Web App
6. **WEBAPP_GUIDE.md** - How to use the interface
7. **WEBAPP_VISUAL_GUIDE.md** - What you'll see

### For Problems
8. **TROUBLESHOOTING.md** - All solutions

### For Reference
9. **README.md** - Full documentation
10. **ARCHITECTURE.md** - Technical details

## Execution Order

```
1. Extract zip
   └── iceberg-demo/ (all files)

2. Navigate to directory
   └── cd iceberg-demo/

3. Start services
   └── docker-compose up -d
   └── Creates: chroma-data/, ollama-data/, localstack-data/

4. Initialize data (FIRST TIME ONLY)
   └── docker exec -it iceberg-app python /app/scripts/demo.py
   └── Populates Chroma DB and Iceberg tables

5. Use the system
   ├── Web: http://localhost:8501
   └── CLI: docker exec -it iceberg-app python /app/scripts/query.py
```

## File Dependencies

```
docker-compose.yml
├── Requires: app/streamlit_app.py (for webapp)
├── Requires: docker/app/Dockerfile (for app container)
└── Creates: 6 containers

scripts/demo.py
├── Connects to: LocalStack (S3)
├── Connects to: Spark (Iceberg)
├── Connects to: Chroma (vectors)
├── Connects to: Ollama (embeddings)
└── Must run BEFORE using web app or query.py

app/streamlit_app.py
├── Connects to: Chroma (reads products)
├── Connects to: Ollama (generates responses)
└── Requires: demo.py run first (for data)
```

## What Gets Created at Runtime

```
After "docker-compose up -d":
├── chroma-data/          # Chroma persistence
├── ollama-data/          # Downloaded models (~2GB)
│   ├── models/
│   │   ├── nomic-embed-text/
│   │   └── llama3.2:1b/
├── localstack-data/      # S3 buckets
│   └── data/
│       └── iceberg-warehouse/
└── Docker volumes        # Container data

After "demo.py":
├── chroma-data/
│   └── products collection (6 products with embeddings)
└── localstack-data/
    └── iceberg-warehouse/
        └── warehouse/
            └── products_db/
                └── products/ (Iceberg table)
```

## Total Size Requirements

### Initial Download
- Package: 71 KB
- Docker images: ~3 GB (on first pull)

### After Setup
- Ollama models: ~2 GB
- Application data: ~100 MB
- Container overhead: ~500 MB

**Total: ~6 GB**

## Quick Command Reference

```bash
# Navigate
cd iceberg-demo/

# View structure
dir                          # Windows
ls -la                       # Mac/Linux

# Check files
dir app                      # Should show: streamlit_app.py, Dockerfile
dir scripts                  # Should show: demo.py, query.py, etc.

# Start
docker-compose up -d

# Initialize (REQUIRED FIRST TIME)
docker exec -it iceberg-app python /app/scripts/demo.py

# Use
make webapp                  # Open web interface
make query                   # CLI queries
make health                  # Check status
make help                    # All commands
```

## Validation Checklist

Before running, verify:
- [ ] All 14 .md files present
- [ ] app/ directory exists with 2 files
- [ ] scripts/ directory exists with 5 files
- [ ] docker/ directory exists
- [ ] docker-compose.yml exists
- [ ] Makefile exists

```bash
# Quick check (Windows PowerShell):
@(
    "app/streamlit_app.py",
    "app/Dockerfile",
    "scripts/demo.py",
    "scripts/query.py",
    "docker-compose.yml",
    "Makefile"
) | ForEach-Object {
    if (Test-Path $_) { "✅ $_" } else { "❌ $_ MISSING" }
}

# Quick check (Mac/Linux):
for file in app/streamlit_app.py app/Dockerfile scripts/demo.py docker-compose.yml; do
    [ -f "$file" ] && echo "✅ $file" || echo "❌ $file MISSING"
done
```

## ZIP Contents

```
Total: 28 items (22 files, 6 directories)

Files by type:
- Markdown docs: 14 files
- Python scripts: 6 files (including webapp)
- Docker configs: 3 files (compose + Dockerfiles)
- Build files: 2 files (Makefile, .gitignore)
- Empty directories: 3 (created for organization)
```

---

## 🎯 Quick Start Path

```
1. Extract → iceberg-demo/
2. cd iceberg-demo/
3. docker-compose up -d
4. Wait 2 minutes
5. docker exec -it iceberg-app python /app/scripts/demo.py
6. Wait 5-10 minutes (first time)
7. Open http://localhost:8501
8. Enjoy! 🎉
```

---

**Need help?** Check START_HERE.md for navigation or QUICK_FIX.md if you have errors!
