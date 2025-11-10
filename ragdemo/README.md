
# LangChain RAG (Retrieval-Augmented Generation) Embedding Builder

This Python script creates a **local vector database** from text files to enable accurate, source-grounded question answering. Here's what it does:

## **Core Purpose**
Builds a searchable knowledge base by converting text documents into vector embeddings stored in ChromaDB, enabling semantic search for RAG applications.

---

## **Key Functions & Components**

### **1. Document Loading (`load_text_files`)**
- Reads multiple text files from disk
- Converts each file into a LangChain `Document` object
- Attaches metadata (source file path) for traceability
- Handles missing files gracefully with warnings
- Uses UTF-8 encoding with error tolerance

### **2. Text Chunking (`RecursiveCharacterTextSplitter`)**
- **Chunk size**: 800 characters (configurable)
- **Chunk overlap**: 120 characters (prevents context loss at boundaries)
- **Smart splitting**: Uses hierarchical separators (`\n\n` → `\n` → space → character)
- Maintains semantic coherence by respecting paragraph/sentence boundaries
- Creates manageable pieces for embedding and retrieval

### **3. Embedding Generation (`HuggingFaceEmbeddings`)**
- Uses **sentence-transformers/all-MiniLM-L6-v2** model
- Runs **locally** (no API calls, free, private)
- Converts text chunks into 384-dimensional vectors
- Captures semantic meaning (similar concepts have similar vectors)

### **4. Vector Storage (`Chroma`)**
- Persists embeddings to disk (`./chroma_db` by default)
- Supports **incremental updates** (add new documents without rebuilding)
- Organizes data into named collections
- Enables fast similarity search via vector operations

### **5. Command-Line Interface**
- `--files`: Input text files to process
- `--persist`: Database storage location
- `--collection`: Named collection for organization
- `--reset`: Clear existing database
- `--chunk_size` / `--chunk_overlap`: Fine-tune chunking behavior

---

## **How This Reduces Hallucinations & False Responses**

### **🎯 Grounding in Source Material**
- AI retrieves **actual document content** before answering
- Responses cite specific text chunks, not invented facts
- Eliminates making up information not in the knowledge base

### **🔍 Semantic Search Precision**
- Finds contextually relevant passages using meaning, not just keywords
- Returns **top-k most similar chunks** to the query
- Provides specific, relevant context to the LLM

### **📚 Source Attribution**
- Metadata tracks which file each chunk came from
- Enables citation of sources in responses
- Users can verify information against original documents

### **🧩 Optimal Context Windows**
- Chunking ensures manageable text pieces fit in LLM context
- Overlap prevents losing information at chunk boundaries
- Balances specificity vs. comprehensiveness

### **💾 Persistent Knowledge Base**
- Creates a **static, verifiable** reference library
- No reliance on LLM's potentially outdated training data
- Can update database as source documents change

### **🔒 Local & Deterministic**
- Embeddings generated consistently from source files
- No external API variability
- Full control over knowledge base content

---

## **Typical RAG Workflow Using This Script**

1. **Build database**: Run this script on your documents
2. **User asks question**: Submit query to your RAG system
3. **Semantic search**: Find relevant chunks from ChromaDB
4. **Context injection**: Pass retrieved chunks + query to LLM
5. **Grounded response**: LLM answers based on provided context, not imagination

**Example**: Instead of asking Claude "What's in my company's policy?", the RAG system retrieves the actual policy text, then asks: "Based on this policy: [retrieved text], answer: What's in my company's policy?"

This dramatically reduces hallucinations by giving the LLM **facts to work with** rather than forcing it to guess.

# LangChain RAG Query System with Ollama

This script performs **semantic search** on the vector database and optionally generates grounded answers using a local Ollama LLM. Here's the complete workflow:

---

## **Core Purpose**
Queries the ChromaDB vector store to find relevant document chunks, then feeds them to Ollama for accurate, source-based answers.

---

## **Key Components & Flow**

### **1. Query Embedding Process**
- **User's question** is converted to a vector using the **same embedding model** (all-MiniLM-L6-v2)
- Creates a 384-dimensional vector representing the semantic meaning of the query
- **Critical**: Uses identical model as ingestion to ensure compatibility
- Query embedding is comparable to document embeddings in vector space

### **2. Similarity Search (`vectordb.similarity_search`)**
- **Calculates cosine similarity** between query vector and all document vectors
- Ranks chunks by semantic relevance (not keyword matching)
- Returns **top-k most similar chunks** (default k=4)
- **Example**: Query "refund policy" finds chunks about returns/refunds even if they don't use that exact word

### **3. Retrieval Results Display**
- Shows top matches with source file attribution
- Displays preview of each retrieved chunk (first 280 characters)
- Allows verification of relevance before LLM processing
- Can run in **retrieval-only mode** (without Ollama)

### **4. Context Preparation for LLM**
- Concatenates all retrieved chunks into a single context block
- Preserves source metadata for each chunk
- Formats as structured prompt: `QUESTION + CONTEXT`
- Creates a self-contained knowledge base for the LLM

### **5. Ollama Integration (Optional)**
- **Runs LLM locally** (no cloud APIs, private, free)
- Common models: `llama3`, `mistral`, `phi3`, etc.
- Receives structured prompt with retrieved context
- Generates answer **constrained to provided context**

### **6. Prompt Engineering for Accuracy**
```
"Using only the CONTEXT below, answer the QUESTION clearly."
"If the answer cannot be found, say you don't know."
```
- Explicitly instructs LLM to **not hallucinate**
- Encourages admission of uncertainty
- Grounds response in provided documents only

---

## **How Vector Embeddings Enable the Query**

### **🔢 Vector Similarity Math**
1. **Query**: "What are the warranty terms?" → `[0.23, -0.45, 0.67, ...]` (384 dims)
2. **Doc Chunk 1**: "90-day warranty covers..." → `[0.25, -0.42, 0.65, ...]` (384 dims)
3. **Doc Chunk 2**: "Shipping policy..." → `[-0.10, 0.30, -0.15, ...]` (384 dims)
4. **Cosine similarity**: Chunk 1 = 0.92 (high), Chunk 2 = 0.31 (low)
5. **Returns**: Chunk 1 ranked first

### **🎯 Semantic Understanding**
- **Synonyms matched**: "refund" finds "reimbursement", "money back"
- **Concepts matched**: "cancellation" finds "termination", "end contract"
- **Context-aware**: "Python snake" vs "Python programming" distinguished by surrounding words in chunks

### **⚡ Speed & Efficiency**
- Vector operations are **extremely fast** (matrix multiplication)
- No need to scan every document linearly
- Chromadb uses optimized indexing (HNSW algorithm)
- Can handle millions of chunks with subsecond queries

---

## **Complete RAG Workflow Example**

### **Scenario**: User asks "How do I return a defective product?"

1. **Query Embedding**
   - Question converted to vector: `[0.12, -0.34, 0.56, ...]`

2. **Similarity Search**
   - Compares against 1,000+ document chunk vectors
   - Finds top 4 matches:
     - Chunk A: "Return Policy - Defective items..." (score: 0.89)
     - Chunk B: "Warranty covers manufacturing..." (score: 0.85)
     - Chunk C: "Contact support@company.com..." (score: 0.78)
     - Chunk D: "30-day return window..." (score: 0.76)

3. **Context Assembly**
   ```
   Source: policies.txt
   Return Policy - Defective items can be returned within 30 days...
   
   Source: warranty.txt
   Warranty covers manufacturing defects for 90 days...
   
   [chunks C & D...]
   ```

4. **Ollama Prompt**
   ```
   QUESTION: How do I return a defective product?
   
   CONTEXT: [above chunks]
   
   Answer using only the context.
   ```

5. **Grounded Answer**
   ```
   For defective products, you can return them within 30 days 
   of purchase. Contact support@company.com with your order number. 
   Manufacturing defects are covered under our 90-day warranty.
   ```

---

## **How This Reduces Hallucinations**

### **✅ Information Retrieval First**
- LLM never generates answers from memory alone
- Always provides source material before asking
- **Pre-RAG**: "What's the return policy?" → LLM guesses
- **With RAG**: "Here's the actual policy [text]. Now answer."

### **✅ Explicit Constraints**
- Prompt tells LLM: "Use **ONLY** this context"
- Encourages "I don't know" when context insufficient
- Reduces confident fabrication of plausible-sounding lies

### **✅ Source Traceability**
- Each chunk includes file metadata
- Can cite specific sources in answer
- Users can verify claims against original documents

### **✅ Recency & Accuracy**
- Knowledge base reflects actual current documents
- Not limited to LLM's training data cutoff
- Update database = update answers (no retraining)

### **✅ Domain Specificity**
- Can include proprietary/private information
- Not dependent on public internet data
- Tailored to your specific use case

---

## **Command-Line Usage Examples**

**Retrieval only** (no Ollama):
```bash
./query.py --query "What's the refund policy?" --k 5
```

**Full RAG with Ollama**:
```bash
./query.py --query "How long is the warranty?" --ollama llama3 --k 3
```

**Custom database**:
```bash
./query.py --persist ./my_docs_db --collection legal --query "Contract terms?" --ollama mistral
```


## **Key Parameters**

- **`--query`**: Natural language question (required)
- **`--k`**: Number of chunks to retrieve (more context vs. noise tradeoff)
- **`--ollama`**: Local model name (enables answer generation)
- **`--persist`**: Vector database location
- **`--collection`**: Named collection within database

**Result**: Accurate, verifiable answers grounded in your actual documents, with full local privacy and no hallucination risk.

# Run Demo 

# 1) Create and activate a venv (recommended)
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Prepare some .txt files (example)
mkdir -p docs
printf "Welcome to the demo.\nRefunds are processed within 7 days." > docs/policy.txt
printf "Meeting notes: prioritize onboarding and docs.\n" > docs/notes.txt

# 4) Build embeddings into a persistent Chroma store
python ingest.py --persist ./chroma_db --collection demo --files docs/policy.txt docs/notes.txt

# 5a) Retrieve similar chunks
python query.py --persist ./chroma_db --collection demo --query "How long do refunds take?"

```
python query.py --persist ./chroma_db --collection demo --query "How long do refunds take?"  --ollama tinyllama
[INFO] Loading Chroma DB…
[INFO] Searching top-4 for: 'How long do refunds take?'

=== Top Matches ===
[1] Source: C:\Users\zcstr\AIDemos\ragdemo\docs\policy.txt
    "Welcome to the demo. The policy is Refunds are processed within 7 days."...

[2] Source: C:\Users\zcstr\AIDemos\ragdemo\docs\policy.txt
    "Welcome to the demo.\nRefunds are processed within 7 days."...

[3] Source: C:\Users\zcstr\AIDemos\ragdemo\docs\policy.txt
    "Welcome to the demo.\nRefunds are processed within 7 days."...

[4] Source: C:\Users\zcstr\AIDemos\ragdemo\docs\notes.txt
    "Meeting notes: prioritize onboarding and docs.\n"...

[INFO] Asking local LLM via Ollama: tinyllama

=== Answer ===
As per the CONTEXT provided, refunds take approximately 7 days to process in this AI demo.
```

# 5b) (Optional) Ask a local LLM via Ollama (if you have a model pulled)
# ollama pull llama3    # run once
python query.py --persist ./chroma_db --collection demo --query "Summarize the policy" --ollama llama3
