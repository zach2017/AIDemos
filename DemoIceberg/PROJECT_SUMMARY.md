# Apache Iceberg Data Lake Demo - Complete Package

## 📦 What's Included

This is a **production-ready, complete Apache Iceberg demo** that integrates:

- **Apache Iceberg** - Modern table format for huge analytic datasets
- **LocalStack** - AWS S3 emulation for local development
- **Chroma Vector Database** - Semantic search capabilities
- **Ollama** - Local LLM for embeddings and question answering
- **Apache Spark** - Data processing engine

## 🎯 Key Features Demonstrated

### 1. Data Lake Operations
- ✅ Create and manage Iceberg tables in S3
- ✅ ACID transactions
- ✅ Schema evolution without downtime
- ✅ Time travel queries (query historical data)
- ✅ Partition management

### 2. Vector Search & RAG
- ✅ Generate embeddings with Ollama
- ✅ Store embeddings in Chroma
- ✅ Semantic search across products
- ✅ Context-aware question answering

### 3. Local Development
- ✅ No cloud costs - everything runs locally
- ✅ No external API dependencies
- ✅ Complete Docker Compose setup
- ✅ Production-like architecture

## 📁 Project Structure

```
iceberg-demo/
├── README.md                    # Comprehensive documentation
├── QUICKSTART.md               # 5-minute getting started guide
├── docker-compose.yml          # Service orchestration
├── Makefile                    # Convenient command shortcuts
├── .gitignore                  # Git ignore rules
│
├── docker/
│   └── app/
│       └── Dockerfile          # Python app container
│
├── scripts/
│   ├── demo.py                 # Main demo (runs everything)
│   ├── query.py                # Interactive Q&A
│   ├── health_check.py         # Service health verification
│   ├── advanced_features.py    # Time travel & schema evolution
│   └── ingest_data.py          # Add new products
│
├── data/                       # Data directory (empty initially)
├── notebooks/                  # Jupyter notebooks (optional)
├── chroma-data/               # Chroma persistence (created at runtime)
├── ollama-data/               # Ollama models (created at runtime)
└── localstack-data/           # LocalStack data (created at runtime)
```

## 🚀 Quick Start (3 Commands)

```bash
# 1. Start services
docker-compose up -d

# 2. Run demo (first run: ~8 mins, includes model download)
docker exec -it iceberg-app python /app/scripts/demo.py

# 3. Ask questions!
docker exec -it iceberg-app python /app/scripts/query.py
```

## 💡 Example Usage Scenarios

### Scenario 1: Interactive Product Search
```bash
make query

# Then ask:
"What laptops do you have for developers?"
"I need furniture for my home office under $500"
"Show me electronics accessories"
```

### Scenario 2: Explore Iceberg Features
```bash
make advanced

# Demonstrates:
- Time travel (query historical data)
- Schema evolution (add columns on the fly)
- Partitioning strategies
```

### Scenario 3: Add New Data
```bash
make ingest

# Interactively add:
- New products
- Update inventory
- Modify pricing
```

### Scenario 4: SQL Queries on Iceberg
```bash
docker exec -it spark-iceberg /bin/bash

# Then run Spark SQL:
SELECT category, COUNT(*) as count, AVG(price) as avg_price
FROM demo.products_db.products
GROUP BY category;
```

## 🎓 What You'll Learn

### Apache Iceberg Concepts
- Table formats and metadata
- Snapshot isolation
- Time travel queries
- Schema evolution
- Partitioning strategies
- ACID guarantees

### Vector Databases
- Embedding generation
- Semantic similarity search
- Metadata filtering
- RAG (Retrieval Augmented Generation)

### Modern Data Stack
- Object storage (S3) for data lakes
- Separation of compute and storage
- Local development practices
- Microservices architecture

## 🛠️ Make Commands Reference

```bash
make help       # Show all commands
make up         # Start services
make down       # Stop services
make demo       # Run full demo
make query      # Interactive Q&A
make health     # Check services
make advanced   # Advanced Iceberg features
make ingest     # Add new products
make logs       # View logs
make clean      # Remove all data
```

## 📊 Sample Queries

### Query 1: Find Products by Category
```sql
SELECT * FROM demo.products_db.products 
WHERE category = 'Electronics' 
ORDER BY price DESC;
```

### Query 2: Price Analysis
```sql
SELECT 
    category,
    COUNT(*) as products,
    AVG(price) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM demo.products_db.products
GROUP BY category;
```

### Query 3: Time Travel (Historical Snapshot)
```sql
SELECT * FROM demo.products_db.products 
VERSION AS OF {snapshot_id};
```

## 🔧 Customization Ideas

### Add Your Own Data
Modify `scripts/demo.py` → `create_sample_data()` function

### Use Different LLM Models
Change in `scripts/demo.py`:
```python
model_name = "nomic-embed-text"  # or "mxbai-embed-large"
chat_model = "llama3.2:1b"       # or "mistral", "phi3"
```

### Connect to Real S3
Update `docker-compose.yml` with real AWS credentials

### Add More Tables
Create new tables with different schemas in Iceberg

### Implement ETL Pipelines
Use Spark to transform and load data

## 🎯 Use Cases

This demo is perfect for:

1. **Learning Data Lakes** - Hands-on with modern table formats
2. **Prototyping RAG Apps** - Build AI apps with local LLMs
3. **Testing Data Pipelines** - Validate ETL logic locally
4. **Training & Workshops** - Teach data engineering concepts
5. **Development** - Test before deploying to cloud

## 📚 Educational Value

### For Data Engineers
- Modern data lake architecture
- Iceberg table format internals
- Object storage patterns
- Schema design and evolution

### For ML Engineers
- Vector database operations
- Embedding generation
- RAG implementation
- Local LLM deployment

### For Students
- Distributed systems concepts
- Microservices architecture
- Docker and containerization
- SQL and data modeling

## ⚙️ System Requirements

- **Docker**: 20.10 or higher
- **Memory**: 8GB minimum (recommend 12GB)
- **Disk**: 10GB free space
- **OS**: Linux, macOS, or Windows (with WSL2)

## 🐛 Common Issues & Solutions

### Issue: Out of Memory
**Solution**: Increase Docker memory to 8GB+ in settings

### Issue: Port Conflicts
**Solution**: Stop services using ports 4566, 8000, 8080, 11434

### Issue: Slow Model Download
**Solution**: First run downloads ~2GB, be patient or use faster internet

### Issue: Services Not Starting
**Solution**: 
```bash
docker-compose down -v  # Clean restart
docker-compose up -d
```

## 🌟 Advanced Topics

Once comfortable with basics, explore:

1. **Multi-catalog Setup** - Use Hive or REST catalog
2. **Streaming Ingestion** - Use Kafka + Spark Streaming
3. **Data Quality** - Implement validation rules
4. **Performance Tuning** - Optimize partitions and file sizes
5. **Security** - Add authentication and encryption

## 📖 Further Reading

- [Apache Iceberg Docs](https://iceberg.apache.org/docs/latest/)
- [Chroma Docs](https://docs.trychroma.com/)
- [Ollama Model Library](https://ollama.ai/library)
- [LocalStack Docs](https://docs.localstack.cloud/)

## 🤝 Next Steps

1. ✅ Run the demo
2. ✅ Experiment with queries
3. ✅ Try advanced features
4. ✅ Add your own data
5. ✅ Extend with new capabilities

## 💬 Questions?

- Check README.md for detailed docs
- Review QUICKSTART.md for fast setup
- Examine scripts/ for code examples
- Run `make help` for command reference

---

**Ready to build modern data lakes? Start with `make up`! 🚀**

## ✨ What Makes This Demo Special

- ✅ **Complete** - All components integrated and working
- ✅ **Educational** - Heavily commented with explanations
- ✅ **Practical** - Real-world patterns and best practices
- ✅ **Extensible** - Easy to modify and expand
- ✅ **Free** - No cloud costs, no API keys needed
- ✅ **Fast** - Get started in minutes

Enjoy exploring the future of data lakes! 🎉
