# Apache Iceberg Data Lake Demo

A comprehensive demo showcasing Apache Iceberg, LocalStack S3, Chroma Vector Database, and Ollama LLM working together to create a modern data lake with RAG (Retrieval Augmented Generation) capabilities.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Compose                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌────────┐   ┌─────────┐  │
│  │LocalStack│   │  Spark   │   │ Chroma │   │ Ollama  │  │
│  │   (S3)   │◄──┤ Iceberg  │──►│Vector  │◄──┤  LLM    │  │
│  │          │   │          │   │   DB   │   │         │  │
│  └──────────┘   └──────────┘   └────────┘   └─────────┘  │
│       │              │              │             │         │
│       └──────────────┴──────────────┴─────────────┘         │
│                         │                                   │
│                    ┌────▼────┐                              │
│                    │   App   │                              │
│                    │Container│                              │
│                    └─────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Components

- **LocalStack**: Emulates AWS S3 locally for Iceberg storage
- **Apache Iceberg**: Open table format for huge analytic datasets
- **Apache Spark**: Processes and queries Iceberg tables
- **Chroma**: Vector database for semantic search
- **Ollama**: Local LLM for embeddings and question answering

## 📋 Prerequisites

- Docker and Docker Compose
- At least 8GB RAM available for Docker
- 10GB free disk space

## 🛠️ Setup

### 1. Clone or Navigate to Project Directory

```bash
cd iceberg-demo
```

### 2. Start All Services

```bash
docker-compose up -d
```

This will start:
- LocalStack (S3) on port 4566
- Spark with Iceberg on ports 8888, 8080, 10000-10001
- Chroma on port 8000
- Ollama on port 11434
- App container for running scripts

### 3. Wait for Services to Initialize

Check service status:
```bash
docker-compose ps
```

All services should show "running" status. This may take 2-3 minutes.

### 4. Run the Demo

```bash
docker exec -it iceberg-app python /app/scripts/demo.py
```

This script will:
1. ✅ Create an S3 bucket in LocalStack
2. ✅ Initialize Spark with Iceberg configuration
3. ✅ Create a products database and table in Iceberg
4. ✅ Load sample product data
5. ✅ Pull Ollama models (nomic-embed-text, llama3.2:1b)
6. ✅ Generate embeddings for all products
7. ✅ Store embeddings in Chroma vector database
8. ✅ Run sample queries demonstrating RAG capabilities

**Note:** First run will take 5-10 minutes as it downloads Ollama models (~2GB).

## 💬 Interactive Querying

After running the demo, you can ask your own questions:

```bash
# Interactive mode
docker exec -it iceberg-app python /app/scripts/query.py

# Or pass a question directly
docker exec -it iceberg-app python /app/scripts/query.py "What laptops do you have?"
```

Example questions:
- "What products do you have for home office?"
- "Show me electronics under $100"
- "I need ergonomic furniture"
- "What's the cheapest product in stock?"

## 📊 Querying Iceberg Tables with Spark

Access the Spark container:
```bash
docker exec -it spark-iceberg /bin/bash
```

Start Spark SQL shell:
```bash
spark-sql --conf spark.sql.catalog.demo=org.apache.iceberg.spark.SparkCatalog \
          --conf spark.sql.catalog.demo.type=hadoop \
          --conf spark.sql.catalog.demo.warehouse=s3a://iceberg-warehouse/warehouse \
          --conf spark.hadoop.fs.s3a.endpoint=http://localstack:4566 \
          --conf spark.hadoop.fs.s3a.access.key=test \
          --conf spark.hadoop.fs.s3a.secret.key=test \
          --conf spark.hadoop.fs.s3a.path.style.access=true
```

Run SQL queries:
```sql
-- Show all products
SELECT * FROM demo.products_db.products;

-- Products by category
SELECT category, COUNT(*) as count, AVG(price) as avg_price 
FROM demo.products_db.products 
GROUP BY category;

-- Find products in stock under $100
SELECT name, price, stock 
FROM demo.products_db.products 
WHERE price < 100 AND stock > 0 
ORDER BY price;

-- View table metadata
DESCRIBE EXTENDED demo.products_db.products;
```

## 🔍 Exploring Components

### LocalStack S3

Check S3 contents:
```bash
docker exec -it iceberg-app python -c "
import boto3
s3 = boto3.client('s3', endpoint_url='http://localstack:4566', 
                  aws_access_key_id='test', aws_secret_access_key='test')
print('Buckets:', s3.list_buckets()['Buckets'])
print('Objects:', s3.list_objects_v2(Bucket='iceberg-warehouse'))
"
```

### Chroma Vector Database

```bash
docker exec -it iceberg-app python -c "
import chromadb
client = chromadb.HttpClient(host='chroma', port=8000)
collection = client.get_collection('products')
print(f'Collection has {collection.count()} documents')
print('Sample:', collection.peek())
"
```

### Ollama Models

List available models:
```bash
docker exec -it ollama ollama list
```

Test Ollama directly:
```bash
docker exec -it ollama ollama run llama3.2:1b "What is Apache Iceberg?"
```

## 📁 Project Structure

```
iceberg-demo/
├── docker-compose.yml          # Service orchestration
├── docker/
│   └── app/
│       └── Dockerfile          # Python app container
├── scripts/
│   ├── demo.py                 # Main demo script
│   └── query.py                # Interactive query tool
├── data/                       # Local data directory
├── notebooks/                  # Jupyter notebooks (optional)
├── chroma-data/               # Chroma persistence
├── ollama-data/               # Ollama models cache
└── localstack-data/           # LocalStack persistence
```

## 🎯 What This Demo Shows

1. **Data Lake with Iceberg**
   - Schema evolution
   - Time travel capabilities
   - ACID transactions
   - S3 as storage backend

2. **Vector Search with Chroma**
   - Semantic similarity search
   - Embedding storage and retrieval
   - Metadata filtering

3. **RAG with Ollama**
   - Local LLM inference
   - Context-aware responses
   - No external API dependencies

4. **Integration**
   - Iceberg → Chroma (data pipeline)
   - Chroma → Ollama (RAG pattern)
   - LocalStack (local cloud development)

## 🧹 Cleanup

Stop all services:
```bash
docker-compose down
```

Remove all data (including Ollama models):
```bash
docker-compose down -v
rm -rf chroma-data ollama-data localstack-data
```

## 🐛 Troubleshooting

### Services not starting
```bash
# Check logs
docker-compose logs -f

# Restart specific service
docker-compose restart ollama
```

### Out of memory
Increase Docker memory allocation to at least 8GB in Docker Desktop settings.

### Ollama model download fails
```bash
# Download models manually
docker exec -it ollama ollama pull nomic-embed-text
docker exec -it ollama ollama pull llama3.2:1b
```

### Chroma connection issues
```bash
# Restart Chroma
docker-compose restart chroma

# Check Chroma logs
docker-compose logs chroma
```

## 🔧 Customization

### Add Your Own Data

Edit `scripts/demo.py` and modify the `create_sample_data()` function to include your own products or data.

### Use Different Ollama Models

In `scripts/demo.py`, change the model names:
```python
# For embeddings
model_name = "nomic-embed-text"  # or "mxbai-embed-large"

# For chat
chat_model = "llama3.2:1b"  # or "mistral", "phi3", etc.
```

### Configure Iceberg

Modify Spark configurations in `docker-compose.yml` or `scripts/demo.py` to change:
- Catalog type (Hadoop, Hive, REST)
- Storage location
- Partitioning strategy

## 📚 Learn More

- [Apache Iceberg Documentation](https://iceberg.apache.org/)
- [Chroma Documentation](https://docs.trychroma.com/)
- [Ollama Documentation](https://ollama.ai/)
- [LocalStack Documentation](https://docs.localstack.cloud/)
- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)

## 📄 License

This demo is provided as-is for educational purposes.

## 🤝 Contributing

Feel free to extend this demo with:
- More complex Iceberg schemas
- Additional Ollama models
- Real-time data ingestion
- Advanced RAG patterns
- Multi-modal embeddings

---

**Enjoy exploring your local data lake! 🎉**
