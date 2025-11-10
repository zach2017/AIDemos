# Architecture Diagram

## Data Flow Overview

```
                     Apache Iceberg Data Lake Demo
                     ==============================

┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                          USER INTERFACE                             │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   Make       │  │   Docker     │  │   Python     │            │
│  │   Commands   │  │   Exec       │  │   Scripts    │            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
│         │                  │                  │                     │
└─────────┼──────────────────┼──────────────────┼─────────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     DOCKER COMPOSE NETWORK                          │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                   Application Container                        │ │
│  │  ┌────────────────────────────────────────────────────┐       │ │
│  │  │  Python Scripts:                                   │       │ │
│  │  │  • demo.py          - Main orchestrator           │       │ │
│  │  │  • query.py         - RAG interface               │       │ │
│  │  │  • health_check.py  - Service monitoring          │       │ │
│  │  │  • advanced_features.py - Iceberg demos           │       │ │
│  │  │  • ingest_data.py   - Data ingestion              │       │ │
│  │  └────────────────────────────────────────────────────┘       │ │
│  │                                                                │ │
│  │         ┌──────────┬──────────┬──────────┬──────────┐         │ │
│  └─────────┤          │          │          │          ├─────────┘ │
│            │          │          │          │          │           │
│            ▼          ▼          ▼          ▼          ▼           │
│  ┌─────────────┐ ┌─────────┐ ┌────────┐ ┌──────────────┐         │
│  │             │ │         │ │        │ │              │         │
│  │ LocalStack  │ │  Spark  │ │ Chroma │ │    Ollama    │         │
│  │    (S3)     │ │ Iceberg │ │Vector  │ │     LLM      │         │
│  │             │ │         │ │   DB   │ │              │         │
│  └─────────────┘ └─────────┘ └────────┘ └──────────────┘         │
│       │              │            │            │                   │
│       │              │            │            │                   │
└───────┼──────────────┼────────────┼────────────┼───────────────────┘
        │              │            │            │
        ▼              ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         PERSISTENT STORAGE                          │
│                                                                     │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐     │
│  │ localstack │  │  Iceberg │  │  chroma  │  │   ollama    │     │
│  │   -data/   │  │  tables  │  │  -data/  │  │   -data/    │     │
│  │            │  │  (in S3) │  │          │  │             │     │
│  │ S3 Buckets │  │ Metadata │  │ Vectors  │  │  Models &   │     │
│  │   & Logs   │  │  & Data  │  │  & Meta  │  │  Embeddings │     │
│  └────────────┘  └──────────┘  └──────────┘  └─────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. LocalStack (S3 Emulation)
**Purpose**: Provides S3-compatible object storage locally
**Port**: 4566
**Data**: Stores Iceberg table files and metadata
**Benefit**: No AWS costs, fast development

### 2. Spark with Iceberg
**Purpose**: SQL engine for querying and managing Iceberg tables
**Ports**: 8888 (Jupyter), 8080 (UI), 10000-10001 (Thrift)
**Capabilities**: 
- Create/manage Iceberg tables
- Run SQL queries
- Time travel
- Schema evolution
- ACID transactions

### 3. Chroma Vector Database
**Purpose**: Stores and searches vector embeddings
**Port**: 8000
**Features**:
- Semantic similarity search
- Metadata filtering
- Persistent storage
- Fast retrieval

### 4. Ollama
**Purpose**: Local LLM for embeddings and text generation
**Port**: 11434
**Models**:
- nomic-embed-text: Embeddings
- llama3.2:1b: Text generation
**Benefit**: No external API calls, privacy-friendly

### 5. Application Container
**Purpose**: Orchestrates all components
**Features**:
- Python scripts for demo
- Spark/Iceberg integration
- Chroma client
- Ollama client

## Data Flow Sequence

### Initialization Flow
```
1. User runs: make demo
2. App Container starts demo.py
3. demo.py creates S3 bucket in LocalStack
4. demo.py initializes Spark with Iceberg
5. demo.py creates Iceberg table in S3
6. demo.py loads sample product data
7. demo.py pulls Ollama models
8. For each product:
   a. Generate embedding via Ollama
   b. Store in Chroma with metadata
9. Demo complete - ready for queries!
```

### Query Flow (RAG Pattern)
```
1. User asks: "What laptops do you have?"
2. query.py generates embedding via Ollama
3. Chroma searches similar embeddings
4. Returns top 3 matching products
5. query.py creates context from results
6. Sends context + question to Ollama LLM
7. Ollama generates natural language answer
8. Display answer to user
```

### Data Ingestion Flow
```
1. User runs: make ingest
2. User provides product details
3. ingest_data.py creates DataFrame
4. Spark writes to Iceberg table (S3)
5. Iceberg updates metadata atomically
6. New data immediately queryable
```

## Network Topology

```
Docker Network: iceberg-network (bridge)
   │
   ├── localstack:4566
   ├── spark-iceberg:8888, 8080, 10000-10001
   ├── chroma:8000
   ├── ollama:11434
   └── iceberg-app (no exposed ports)
```

All containers communicate via the `iceberg-network` bridge network.

## Storage Architecture

```
Host Machine
    │
    ├── iceberg-demo/
    │   ├── localstack-data/     ← LocalStack persistence
    │   ├── chroma-data/         ← Chroma vectors
    │   ├── ollama-data/         ← Ollama models (~2GB)
    │   ├── data/                ← Shared data directory
    │   ├── notebooks/           ← Jupyter notebooks
    │   └── scripts/             ← Python scripts
    │
    └── Docker Volumes (managed by Docker)
```

## Technology Stack

```
Frontend Layer:
  └── Command Line Interface (Make, Docker Exec)

Application Layer:
  ├── Python 3.11
  ├── PySpark 3.5.0
  ├── PyIceberg 0.6.1
  ├── ChromaDB Client 0.4.18
  └── Ollama Client 0.1.7

Data Layer:
  ├── Apache Iceberg (Table Format)
  ├── Apache Spark (Query Engine)
  ├── Chroma (Vector Store)
  └── LocalStack S3 (Object Storage)

AI/ML Layer:
  ├── Ollama (LLM Runtime)
  ├── nomic-embed-text (Embeddings)
  └── llama3.2:1b (Text Generation)
```

## Scalability Considerations

### Current Setup (Demo)
- Single node Spark
- Local storage
- Small datasets (< 1GB)
- Suitable for: Development, testing, learning

### Production Path
- Multi-node Spark cluster
- Real S3 (AWS, MinIO, Ceph)
- Distributed Chroma
- Larger Ollama models
- Suitable for: Production workloads

## Security Model

### Current (Development)
- Open ports on localhost
- Default credentials (test/test)
- No authentication
- Suitable for: Local development

### Production Recommendations
- Authentication on all services
- Encrypted connections (TLS)
- Network isolation
- Secrets management
- Access control (IAM, RBAC)

---

**This architecture provides a complete, isolated environment for exploring modern data lake technologies!**
