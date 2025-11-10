# Quick Start Guide

Get up and running with the Apache Iceberg Data Lake demo in 5 minutes!

## 🚀 Fast Track (5 minutes)

```bash
# 1. Start services
docker-compose up -d

# 2. Wait for services (2-3 minutes)
# Watch the logs to see when ready:
docker-compose logs -f

# 3. Check health (optional)
docker exec -it iceberg-app python /app/scripts/health_check.py

# 4. Run the demo (first run: ~8 minutes, includes model download)
docker exec -it iceberg-app python /app/scripts/demo.py

# 5. Open the web app! 🌐
# Visit: http://localhost:8501
# Or run: make webapp

# 6. Or ask questions via CLI
docker exec -it iceberg-app python /app/scripts/query.py
```

## 🎯 Or Use Make Commands

If you have `make` installed:

```bash
make up          # Start services
make health      # Check status
make demo        # Run demo
make webapp      # Open web app 🌐
make query       # Ask questions (CLI)
```

## 🌐 Web Application Features

After running the demo, open the web app at **http://localhost:8501**

The web app provides:

### 🔍 Smart Search Tab
- Ask natural language questions
- See the RAG process in action
- View retrieved products with similarity scores
- Get AI-generated answers with context

### 📦 Product Catalog Tab
- Browse all products
- Filter by category and price
- Sort by various criteria
- View detailed statistics

### 🧪 RAG Process Tab
- Visual comparison: With RAG vs Without RAG
- Interactive embedding demo
- Step-by-step process explanation
- Key concepts and use cases

### 📈 Analytics Tab
- Products by category (charts)
- Price distribution graphs
- Stock level visualization
- Detailed statistics and metrics

**Try it:** After running `make demo`, run `make webapp` to open in your browser!

## 💡 Example Questions to Try

Once the demo is running, try these questions:

```
What laptops do you have for developers?
I need furniture for my home office under $500
Show me electronics accessories
What's the cheapest product in stock?
I need an ergonomic setup for my home office
```

## 📊 Query Iceberg Data Directly

```bash
# Enter Spark container
docker exec -it spark-iceberg /bin/bash

# Run SQL queries
spark-sql --conf spark.sql.catalog.demo=org.apache.iceberg.spark.SparkCatalog \
          --conf spark.sql.catalog.demo.type=hadoop \
          --conf spark.sql.catalog.demo.warehouse=s3a://iceberg-warehouse/warehouse
```

Then try:
```sql
SELECT * FROM demo.products_db.products;
SELECT category, COUNT(*) FROM demo.products_db.products GROUP BY category;
```

## 🧹 Clean Up

```bash
# Stop services
docker-compose down

# Or remove everything including data
make clean
```

## ⚠️ First Run Notes

- **Model Download**: First run downloads ~2GB of Ollama models (takes 5-10 minutes)
- **Memory**: Ensure Docker has at least 8GB RAM allocated
- **Disk**: Needs ~10GB free space for models and data

## 🆘 Troubleshooting

**Services not starting?**
```bash
docker-compose ps    # Check status
docker-compose logs  # Check logs
```

**Out of memory?**
- Increase Docker memory limit in Docker Desktop settings to 8GB+

**Port conflicts?**
- Check if ports 4566, 8000, 8080, 11434 are available

## 📚 What's Next?

After the quick start:
1. Read the full [README.md](README.md) for detailed documentation
2. Explore the scripts in `scripts/` directory
3. Check out individual components:
   - LocalStack S3 for cloud storage emulation
   - Apache Iceberg for data lake features
   - Chroma for vector search
   - Ollama for local LLM inference

---

**Ready to dive deeper?** Check the full [README.md](README.md)!
