#!/usr/bin/env python3
import argparse
import os
import sys
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

try:
    # Correct import from langchain_community
    from langchain_community.llms import Ollama
except ImportError:
    Ollama = None

def main():
    ap = argparse.ArgumentParser()
    # Removed --persist as it's not used for CloudClient
    ap.add_argument("--collection", default="demo", help="Chroma collection name")
    ap.add_argument("--query", required=True, help="Natural-language query")
    ap.add_argument("--k", type=int, default=4, help="Top-k results to fetch")
    ap.add_argument("--ollama", default=None, help="Model name to use via Ollama (optional)")
    args = ap.parse_args()

    if args.ollama and Ollama is None:
        print("[WARN] langchain-community or Ollama not available. Install with: pip install langchain-community")
        print("[WARN] Proceeding with retrieval only.")

    # --- 1. Get Chroma Cloud Credentials ---
    # Load from environment variables
    api_key = os.environ.get("CHROMA_API_KEY")
    tenant = os.environ.get("CHROMA_TENANT")
    database = os.environ.get("CHROMA_DATABASE", "chroma_db") # Default to 'chroma_db' if not set

    if not api_key or not tenant:
        print("[ERROR] CHROMA_API_KEY and CHROMA_TENANT environment variables must be set.")
        sys.exit(1)

    # --- 2. Initialize Chroma Cloud Client (raw client) ---
    print("[INFO] Connecting to Chroma Cloud...")
    client = chromadb.CloudClient(
        api_key=api_key,
        tenant=tenant,
        database='chroma_db'
    )

    print("Connected")
    # --- 3. Initialize Embeddings ---
    # Using HuggingFace, but you could also use local Ollama embeddings here
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # --- 4. Initialize LangChain Wrapper ---
    # Pass the raw client, collection name, and embedding function to the
    # LangChain Chroma wrapper. This is the key fix.
    print("[INFO] Loading Chroma collection via LangChain...")
    vectordb = Chroma(
        client=client,
        collection_name=args.collection,
        embedding_function=embeddings
    )

    # --- 5. Search Documents ---
    print(f"[INFO] Searching top-{args.k} for: {args.query!r}")
    # Now similarity_search will work on the LangChain vectordb object
    docs = vectordb.similarity_search(args.query, k=args.k)

    print("\n=== Top Matches ===")
    for i, d in enumerate(docs, 1):
        src = d.metadata.get("source", "unknown")
        # Ensure page_content is a string before slicing
        content_str = str(d.page_content)
        preview = content_str[:280].replace("\n", " ")
        print(f"[{i}] Source: {src}\n    {preview}...\n")

    # --- 6. (Optional) RAG with Ollama ---
    if args.ollama and Ollama is not None:
        print(f"[INFO] Asking local LLM via Ollama: {args.ollama}")
        llm = Ollama(model=args.ollama) # Use correct class name
        
        context = "\n\n".join([f"Source: {d.metadata.get('source','unknown')}\n{d.page_content}" for d in docs])
        
        prompt = (
            "You are a helpful assistant. Using only the CONTEXT below, answer the QUESTION clearly.\n\n"
            f"QUESTION:\n{args.query}\n\nCONTEXT:\n{context}\n\n"
            "If the answer cannot be found, say you don't know."
        )
        
        print("[INFO] Generating answer...")
        answer = llm.invoke(prompt)
        print("\n=== Answer ===")
        print(answer.strip())

if __name__ == "__main__":
    main()