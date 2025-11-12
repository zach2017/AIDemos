# Flask RAG Application Tutorial

## Table of Contents
1. [Overview](#overview)
2. [Key Concepts](#key-concepts)
3. [Dependencies Explained](#dependencies-explained)
4. [How the Application Works](#how-the-application-works)
5. [ChromaDB & Embeddings Deep Dive](#chromadb--embeddings-deep-dive)
6. [Ollama Integration & RAG Process](#ollama-integration--rag-process)
7. [API Endpoints](#api-endpoints)

---

## Overview

This is a **Flask-based RAG (Retrieval-Augmented Generation) application** that allows users to:
- Upload text documents (txt, md, csv, json, py, js, html, css, log files)
- Process and store documents as vector embeddings in ChromaDB
- Query the knowledge base using semantic similarity search
- Optionally enhance queries with Ollama LLM for intelligent answers

**Use Cases:**
- Build a searchable knowledge base from your documents
- Create a chatbot that answers questions based on your specific documents
- Implement semantic search over large document collections
- RAG-powered Q&A systems

---

## Key Concepts

### 🔹 **Embeddings**
- **What:** Numerical representations (vectors) of text that capture semantic meaning
- **Why:** Allow computers to understand that "dog" and "puppy" are similar, even though the words are different
- **How:** The model converts text like "machine learning" into a 384-dimensional vector: `[0.23, -0.45, 0.67, ...]`
- **Example:** Words with similar meanings have vectors that are close together in vector space

### 🔹 **Vector Database (ChromaDB)**
- **What:** A specialized database that stores and efficiently searches vector embeddings
- **Why:** Traditional databases can't find "similar" content; vector databases excel at semantic similarity
- **How:** Uses algorithms like HNSW (Hierarchical Navigable Small World) for fast approximate nearest neighbor search
- **Analogy:** Like a librarian who groups books by topic, not just alphabetically

### 🔹 **Chunking**
- **What:** Breaking large documents into smaller, manageable pieces
- **Why:** Embeddings work better on focused content; helps with retrieval precision
- **Parameters:**
  - `chunk_size`: 800 characters per chunk (configurable)
  - `chunk_overlap`: 120 characters overlap between chunks to maintain context
- **Example:** A 10-page document might become 50 chunks of ~800 characters each

### 🔹 **RAG (Retrieval-Augmented Generation)**
- **What:** A technique that combines information retrieval with LLM generation
- **Why:** Provides accurate, source-grounded answers instead of potentially hallucinated responses
- **Process:**
  1. User asks a question
  2. System retrieves relevant documents from vector database
  3. LLM generates answer using retrieved context
  4. Result: Accurate answer based on your actual documents

### 🔹 **Semantic Search**
- **What:** Search based on meaning, not just keyword matching
- **Example:** Searching "how to fix a broken pipe" will find documents about "plumbing repair" even if those exact words aren't present

---

## Dependencies Explained

### **Flask**
```
Purpose: Web framework for building the HTTP API server
Role: Handles routing, request/response, file uploads
Why: Provides the web interface for document upload and querying
```

### **langchain-chroma**
```
Purpose: LangChain integration with ChromaDB
Role: Provides Chroma class for creating/loading vector databases
Why: Simplifies ChromaDB operations with LangChain's Document abstraction
Key Functions: Chroma.from_documents(), similarity_search()
```

### **langchain-huggingface**
```
Purpose: Integration with HuggingFace models in LangChain
Role: Provides HuggingFaceEmbeddings class
Why: Allows using HuggingFace's pre-trained embedding models
Model Used: sentence-transformers/all-MiniLM-L6-v2
  - Fast and efficient (384 dimensions)
  - Good balance of speed and quality
  - Optimized for semantic similarity tasks
```

### **langchain-text-splitters**
```
Purpose: Text chunking utilities
Role: Provides RecursiveCharacterTextSplitter
Why: Intelligently splits documents while preserving context
How: Tries to split on paragraph breaks (\n\n), then lines (\n), then spaces
```

### **langchain-core**
```
Purpose: Core LangChain abstractions
Role: Provides Document class for representing text with metadata
Why: Standardized format for passing documents through the pipeline
Structure: Document(page_content="text", metadata={"source": "file.txt"})
```

### **langchain-ollama**
```
Purpose: LangChain integration with Ollama LLMs
Role: Provides OllamaLLM class for calling local Ollama models
Why: Enables RAG by generating answers from retrieved context
Optional: App works without it (provides retrieval only)
```

### **sentence-transformers**
```
Purpose: Library for state-of-the-art sentence embeddings
Role: Underlying library for the HuggingFace embedding model
Why: Provides the actual neural network that converts text to vectors
Models: Pre-trained on large text corpora for general-purpose embeddings
```

### **chromadb**
```
Purpose: The core vector database engine
Role: Stores, indexes, and searches vector embeddings
Why: Fast, lightweight, and embeddable vector database
Features:
  - Persistent storage on disk
  - Multiple collections support
  - Efficient similarity search
  - No separate server required (embedded mode)
```

### **Werkzeug**
```
Purpose: WSGI utility library (comes with Flask)
Role: Handles file uploads, security (secure_filename)
Why: Sanitizes uploaded filenames to prevent security issues
```

### **requests**
```
Purpose: HTTP library for making API calls
Role: Checks Ollama availability by querying its API
Why: Detects available Ollama models at runtime
```

---

## How the Application Works

### **1. Document Upload & Processing Flow**

```
User Uploads Files
       ↓
Flask receives files (/upload endpoint)
       ↓
Files saved temporarily to ./uploads/
       ↓
load_text_files() reads file contents
       ↓
Creates Document objects with metadata
       ↓
RecursiveCharacterTextSplitter chunks documents
  - Chunk size: 800 characters
  - Overlap: 120 characters
  - Preserves context across boundaries
       ↓
HuggingFaceEmbeddings converts each chunk to vector
  - Model: all-MiniLM-L6-v2
  - Output: 384-dimensional vectors
       ↓
ChromaDB stores vectors with metadata
  - Persisted to ./chroma_db/
  - Organized by collection name
       ↓
Temporary files cleaned up
       ↓
Returns success response with stats
```

**Example:**
```
Input: "The quick brown fox jumps over the lazy dog." (repeated 100 times)
       ↓
Output: ~5 chunks (depending on exact length)
Each chunk → 384-dimensional vector → stored in ChromaDB
```

### **2. Query & Search Flow**

```
User Submits Query
       ↓
Query text embedded using same model
  - "What is machine learning?" → [0.12, -0.34, 0.56, ...]
       ↓
ChromaDB similarity search
  - Compares query vector to all stored vectors
  - Uses cosine similarity or distance metric
  - Returns k=4 most similar chunks (configurable)
       ↓
Results formatted with metadata
       ↓
Optional: Ollama RAG Enhancement
  - Concatenates retrieved chunks as context
  - Sends prompt + context to Ollama LLM
  - LLM generates natural language answer
       ↓
Returns results + optional LLM answer
```

**Similarity Calculation:**
```
Query: "How do I train a neural network?"
       ↓ (embedded)
Vector: [0.1, 0.5, -0.3, ...]
       ↓ (compared to all stored vectors)
Chunk 1: "Neural network training involves..." - Similarity: 0.87
Chunk 2: "Deep learning requires GPUs for..." - Similarity: 0.81
Chunk 3: "To train models, use gradient descent..." - Similarity: 0.79
Chunk 4: "Backpropagation is the key algorithm..." - Similarity: 0.75
       ↓
Returns top 4 chunks
```

---

## ChromaDB & Embeddings Deep Dive

### **How ChromaDB Stores Embeddings**

1. **Collection Structure:**
   ```
   ./chroma_db/
   └── demo/  (collection name)
       ├── chroma.sqlite3  (metadata & document storage)
       ├── index/  (HNSW index for fast search)
       └── data_level0.bin  (vector data)
   ```

2. **Each Stored Item Contains:**
   - **Vector:** 384 floats representing semantic meaning
   - **Document:** Original text chunk
   - **Metadata:** Source filename, chunk ID, etc.
   - **ID:** Unique identifier for the chunk

3. **Indexing:**
   - ChromaDB builds an HNSW index for O(log n) search complexity
   - Without index: Must compare query to ALL vectors (slow)
   - With index: Navigates graph structure (fast)

### **Embedding Process Explained**

**Step-by-step: Text → Vector**

```python
# Original text
text = "Machine learning is a subset of artificial intelligence."

# Tokenization
tokens = ["machine", "learning", "is", "a", "subset", "of", "artificial", "intelligence"]

# Neural network processing (simplified)
# 1. Each token → initial embedding
# 2. Transformer layers capture context
# 3. Pooling (e.g., mean) → single vector

# Result
vector = [0.23, -0.45, 0.67, 0.12, -0.89, ...]  # 384 dimensions
```

**Why This Model (all-MiniLM-L6-v2)?**
- **MiniLM:** Distilled from larger BERT model (faster, smaller)
- **L6:** 6 transformer layers (good speed/quality balance)
- **v2:** Improved version with better training
- **384 dimensions:** Enough to capture semantic meaning
- **Pre-trained:** Ready to use, no training needed

### **Similarity Search Algorithm**

ChromaDB uses **cosine similarity** by default:

```
Cosine Similarity = (A · B) / (||A|| × ||B||)

Where:
- A is the query vector
- B is a stored document vector
- · is dot product
- ||A|| is the magnitude of A

Result: Value between -1 and 1
- 1 = identical meaning
- 0 = orthogonal (unrelated)
- -1 = opposite meaning
```

**Example:**
```python
Query vector:     [0.5, 0.3, -0.2]
Document vector:  [0.4, 0.4, -0.1]

Dot product: (0.5×0.4) + (0.3×0.4) + (-0.2×-0.1) = 0.34
Magnitude A: √(0.5² + 0.3² + 0.2²) = 0.62
Magnitude B: √(0.4² + 0.4² + 0.1²) = 0.57

Cosine similarity: 0.34 / (0.62 × 0.57) = 0.96 (very similar!)
```

---

## Ollama Integration & RAG Process

### **What is Ollama?**
- **Purpose:** Run large language models locally on your machine
- **Models:** Llama 2, Llama 3, Mistral, Phi, Neural-Chat, etc.
- **Why Local:** Privacy, no API costs, no rate limits
- **How:** Optimized inference engine for running LLMs efficiently

### **RAG Process with Ollama**

**Without RAG (Bad):**
```
User: "What are the requirements for our new API?"
LLM: "I don't have information about your specific API requirements."
```

**With RAG (Good):**
```
1. Query: "What are the requirements for our new API?"
2. Retrieve: Find 4 relevant chunks from uploaded requirement docs
3. Context: Combine retrieved chunks into context
4. Prompt: "Using this context: [chunks], answer: [query]"
5. Generate: LLM produces answer grounded in your documents
6. Result: "Based on your requirements document, the API must..."
```

### **How Ollama Works in This App**

```python
# 1. Retrieve relevant chunks
docs = vectordb.similarity_search("What is machine learning?", k=4)

# 2. Build context from retrieved documents
context = """
Source: ml_intro.txt
Machine learning is a subset of AI that enables systems to learn...

Source: ml_algorithms.txt
Common algorithms include neural networks, decision trees...

Source: ml_applications.txt
Applications range from image recognition to natural language...

Source: ml_training.txt
Training involves feeding data to models and adjusting weights...
"""

# 3. Create prompt for Ollama
prompt = f"""
You are a helpful assistant. Using only the CONTEXT below, answer the QUESTION clearly.

QUESTION:
What is machine learning?

CONTEXT:
{context}

If the answer cannot be found in the context, say you don't know.
"""

# 4. Send to Ollama
llm = OllamaLLM(model="llama3")
answer = llm.invoke(prompt)

# 5. Get grounded answer
# "Machine learning is a subset of artificial intelligence that enables
# systems to learn from data without explicit programming. It uses algorithms
# like neural networks and decision trees, with applications in image
# recognition and natural language processing..."
```

### **Key RAG Benefits**

1. **Accuracy:** Answers based on your actual documents
2. **Source Attribution:** Can trace answers back to source docs
3. **Up-to-date:** Information is as current as your uploaded docs
4. **Domain-Specific:** Works with specialized knowledge bases
5. **Hallucination Prevention:** LLM can only use provided context

### **When Ollama is Optional**

The app works in **two modes:**

**Mode 1: Retrieval Only (No Ollama)**
- Returns raw document chunks
- User reads chunks themselves
- Faster, simpler, always works
- Good for: Finding relevant sections, quick lookups

**Mode 2: RAG with Ollama (Enhanced)**
- Returns chunks + natural language answer
- LLM synthesizes information
- Requires Ollama installed and running
- Good for: Question answering, summaries, explanations

---

## API Endpoints

### **POST /upload**
**Purpose:** Upload and process documents into ChromaDB

**Parameters:**
- `files[]`: Multiple files to upload
- `persist_dir`: Where to store ChromaDB (default: ./chroma_db)
- `collection_name`: Name for this collection (default: demo)
- `reset`: true/false - Clear existing collection?
- `chunk_size`: Characters per chunk (default: 800)
- `chunk_overlap`: Overlap between chunks (default: 120)

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed 3 files into 47 chunks",
  "chunks": 47,
  "files": 3
}
```

**Example Usage:**
```javascript
const formData = new FormData();
formData.append('files[]', file1);
formData.append('files[]', file2);
formData.append('collection_name', 'my_docs');
formData.append('chunk_size', '1000');
formData.append('reset', 'false');

fetch('/upload', { method: 'POST', body: formData });
```

---

### **GET /collections**
**Purpose:** List available collections

**Parameters:**
- `persist_dir`: Database directory to check

**Response:**
```json
{
  "collections": ["demo", "my_docs", "project_docs"]
}
```

---

### **POST /query**
**Purpose:** Search the knowledge base and optionally get LLM answer

**Request Body:**
```json
{
  "query": "How do I implement authentication?",
  "persist_dir": "./chroma_db",
  "collection_name": "demo",
  "k": 4,
  "use_ollama": true,
  "ollama_model": "llama3"
}
```

**Parameters:**
- `query`: Your search question
- `persist_dir`: Database location
- `collection_name`: Which collection to search
- `k`: Number of results to retrieve (default: 4)
- `use_ollama`: Enable RAG with LLM (default: false)
- `ollama_model`: Which Ollama model to use

**Response (without Ollama):**
```json
{
  "success": true,
  "count": 4,
  "results": [
    {
      "rank": 1,
      "source": "auth_guide.txt",
      "content": "Authentication implementation starts with...",
      "preview": "Authentication implementation starts with choosing a strategy..."
    },
    // ... more results
  ]
}
```

**Response (with Ollama):**
```json
{
  "success": true,
  "count": 4,
  "results": [...],
  "ollama_answer": "To implement authentication, you should start by choosing between JWT tokens or session-based auth. Based on your docs, JWT is recommended for APIs...",
  "ollama_model": "llama3"
}
```

---

### **GET /ollama/models**
**Purpose:** List available Ollama models

**Response:**
```json
{
  "models": ["llama2", "llama3", "mistral", "phi"],
  "available": true
}
```

---

### **GET /health**
**Purpose:** Check if the service is running

**Response:**
```json
{
  "status": "healthy",
  "ollama_available": true
}
```

---

## Configuration Options

### **Chunk Size & Overlap**

**Chunk Size (800 default):**
- **Too Small (200):** Loses context, many chunks
- **Too Large (2000):** Less precise retrieval
- **Recommended:** 500-1000 for most documents

**Chunk Overlap (120 default):**
- **Purpose:** Prevents splitting important information
- **Example:** If a sentence spans chunk boundary, overlap ensures both chunks include it
- **Recommended:** 10-20% of chunk size

### **Number of Results (k=4)**

- **k=1:** Only best match (risky, might miss context)
- **k=4:** Good balance (default)
- **k=10:** More context for LLM, slower
- **Trade-off:** More results = more context but more noise

### **Collection Names**

Use different collections for:
- Different projects ("project_a", "project_b")
- Different document types ("code", "docs", "emails")
- Different time periods ("2024_q1", "2024_q2")

---

## Complete Example Workflow

### **Scenario: Building a Company Handbook Chatbot**

**Step 1: Upload Documents**
```bash
# Upload employee handbook, policies, and procedures
curl -X POST http://localhost:5000/upload \
  -F "files[]=@handbook.pdf" \
  -F "files[]=@policies.txt" \
  -F "files[]=@procedures.md" \
  -F "collection_name=company_handbook" \
  -F "chunk_size=1000" \
  -F "reset=true"
```

**Step 2: Query Without AI**
```bash
# Find relevant sections about vacation policy
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the vacation policy?",
    "collection_name": "company_handbook",
    "k": 3
  }'

# Returns 3 relevant document chunks
```

**Step 3: Query With AI (RAG)**
```bash
# Get natural language answer
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How much vacation do I get as a new employee?",
    "collection_name": "company_handbook",
    "k": 5,
    "use_ollama": true,
    "ollama_model": "llama3"
  }'

# Returns: "Based on the employee handbook, new employees receive
# 15 days of paid vacation per year, accruing at 1.25 days per month..."
```

---

## Troubleshooting

### **Ollama Not Available**
**Symptom:** `ollama_available: false` in /health
**Solutions:**
1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3`
3. Ensure Ollama is running: `ollama serve`
4. Check port 11434 is accessible

### **No Results Found**
**Symptom:** Empty results array
**Solutions:**
1. Verify documents were uploaded successfully
2. Check collection_name matches
3. Try broader search query
4. Reduce k value (might be fewer than k documents)

### **Poor Search Quality**
**Symptom:** Results don't match query
**Solutions:**
1. Adjust chunk size (try 600-1200)
2. Increase chunk overlap (try 150-200)
3. Upload more diverse documents
4. Rephrase query more specifically

### **Out of Memory**
**Symptom:** Application crashes during upload
**Solutions:**
1. Reduce chunk size to create fewer embeddings
2. Process files in smaller batches
3. Increase chunk_overlap less
4. Upgrade RAM or use smaller embedding model

---

## Advanced Topics

### **Multiple Collections Strategy**

```python
# Organization by purpose
"customer_support" → Customer query docs
"engineering" → Technical documentation
"sales" → Product materials
"hr" → Internal policies

# Organization by time
"docs_2024_q1"
"docs_2024_q2"
"docs_2024_q3"

# Organization by confidentiality
"public_docs"
"internal_docs"
"confidential_docs"
```

### **Embedding Model Alternatives**

**Current:** `all-MiniLM-L6-v2` (384 dim, fast)
**Alternatives:**
- `all-mpnet-base-v2` (768 dim, better quality, slower)
- `multi-qa-MiniLM-L6-cos-v1` (384 dim, optimized for Q&A)
- `paraphrase-multilingual-MiniLM-L12-v2` (384 dim, multilingual)

**To change:**
```python
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)
```

### **Scaling Considerations**

**Small (<1000 docs):** Current setup works great
**Medium (1000-10,000 docs):** Consider batching uploads
**Large (>10,000 docs):** Consider:
- Separate ChromaDB server mode
- Indexing optimization
- Query result caching
- Load balancing

---

## Summary

This Flask application provides a complete RAG pipeline:

1. **Ingestion:** Upload → Chunk → Embed → Store
2. **Retrieval:** Query → Embed → Search → Retrieve
3. **Generation (optional):** Context + Query → LLM → Answer

**Key Technologies:**
- **Flask:** Web framework
- **ChromaDB:** Vector database
- **HuggingFace:** Embedding model
- **LangChain:** Integration glue
- **Ollama:** Local LLM (optional)

**Core Workflow:**
```
Documents → Embeddings → ChromaDB → Similarity Search → (Optional: LLM) → Answers
```

The app enables building powerful, privacy-focused, document-based Q&A systems without requiring external APIs or cloud services.