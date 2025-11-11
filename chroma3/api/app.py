import os
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Optional Ollama
try:
    from langchain_ollama import OllamaLLM
except Exception:
    OllamaLLM = None


# ---------- Config ----------
DOCS_PERSIST_DIR = os.getenv("DOCS_PERSIST_DIR", "/app/data/chroma_docs")
KEYWORDS_PERSIST_DIR = os.getenv("KEYWORDS_PERSIST_DIR", "/app/data/chroma_keywords")
DOCS_COLLECTION = os.getenv("DOCS_COLLECTION", "docs")
KEYWORDS_COLLECTION = os.getenv("KEYWORDS_COLLECTION", "keywords")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://ollama:11434")
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*")

Path(DOCS_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
Path(KEYWORDS_PERSIST_DIR).mkdir(parents=True, exist_ok=True)

# Embeddings (shared)
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

# App
app = FastAPI(title="Ingest & Query (Chroma + Ollama)")

# CORS
allow_origins = [o.strip() for o in CORS_ALLOW_ORIGINS.split(",")] if CORS_ALLOW_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static assets under /web, and return index.html on root
WEB_DIR = "/app/web"
if Path(WEB_DIR).exists():
    app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")


# ---------- Utilities ----------
def get_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", " ", ""],
    )


def get_docs_db():
    return Chroma(
        persist_directory=DOCS_PERSIST_DIR,
        collection_name=DOCS_COLLECTION,
        embedding_function=embeddings,
    )


def get_keywords_db():
    return Chroma(
        persist_directory=KEYWORDS_PERSIST_DIR,
        collection_name=KEYWORDS_COLLECTION,
        embedding_function=embeddings,
    )


def as_docs_from_keywords(raw: str):
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    return [Document(page_content=kw, metadata={"type": "keyword"}) for kw in lines]


def ollama_llm(model: str):
    if not model or OllamaLLM is None:
        return None
    return OllamaLLM(model=model, base_url=OLLAMA_BASE)


# ---------- Health ----------
@app.get("/healthz")
def healthz():
    return {"ok": True}


# ---------- Root (serve SPA) ----------
@app.get("/")
def root_index():
    index_path = Path(WEB_DIR) / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "UI not found. Place index.html under /app/web or open /docs for API."}


# ---------- API: Ingest ----------
@app.post("/api/ingest")
async def ingest(
    files: List[UploadFile] = File(default=[]),
    keywords: Optional[str] = Form(default=None),
    reset_docs: str = Form(default="false"),
    reset_keywords: str = Form(default="false"),
):
    docs_added = 0
    kw_added = 0

    # Reset dirs if requested
    if reset_docs.lower() == "true" and Path(DOCS_PERSIST_DIR).exists():
        for p in Path(DOCS_PERSIST_DIR).iterdir():
            if p.is_file():
                p.unlink()
            else:
                import shutil
                shutil.rmtree(p, ignore_errors=True)

    if reset_keywords.lower() == "true" and Path(KEYWORDS_PERSIST_DIR).exists():
        for p in Path(KEYWORDS_PERSIST_DIR).iterdir():
            if p.is_file():
                p.unlink()
            else:
                import shutil
                shutil.rmtree(p, ignore_errors=True)

    # Ingest documents
    if files:
        raw_docs = []
        for uf in files:
            content = await uf.read()
            try:
                text = content.decode("utf-8", errors="ignore")
            except Exception:
                text = content.decode("latin-1", errors="ignore")
            raw_docs.append(Document(page_content=text, metadata={"filename": uf.filename}))

        splitter = get_splitter()
        chunks = splitter.split_documents(raw_docs)
        db = get_docs_db()
        db.add_documents(chunks)
        docs_added = len(chunks)

    # Ingest keywords
    if keywords:
        kw_docs = as_docs_from_keywords(keywords)
        kw_db = get_keywords_db()
        kw_db.add_documents(kw_docs)
        kw_added = len(kw_docs)

    return {"status": "ok", "docs_chunks_added": docs_added, "keywords_added": kw_added}


# ---------- API: Query ----------
@app.post("/api/query")
async def query(
    query: str = Form(...),
    k: int = Form(4),
    mode: str = Form("both"),  # "docs" | "keywords" | "both"
    ollama_model: Optional[str] = Form(default=None),
):
    mode = (mode or "both").lower()
    results = {}

    if mode in ("docs", "both"):
        docs_db = get_docs_db()
        docs_hits = docs_db.similarity_search(query, k=k)
        results["docs"] = [
            {"preview": d.page_content[:280], "metadata": d.metadata} for d in docs_hits
        ]

    if mode in ("keywords", "both"):
        kw_db = get_keywords_db()
        kw_hits = kw_db.similarity_search(query, k=k)
        results["keywords"] = [
            {"keyword": d.page_content, "metadata": d.metadata} for d in kw_hits
        ]

    # Optional RAG answer from Ollama across both contexts
    rag_answer = None
    if ollama_model:
        llm = ollama_llm(ollama_model)
        if llm:
            ctx_parts = []
            for sect in ("docs", "keywords"):
                for item in results.get(sect, []):
                    if sect == "docs":
                        ctx_parts.append(item["preview"])
                    else:
                        ctx_parts.append(item["keyword"])
            context = "\n\n".join(ctx_parts[: k * 2]) if ctx_parts else ""
            if context:
                prompt = (
                    "Use only the CONTEXT to answer the QUESTION. "
                    "If the answer isn't in the context, say you don't know.\n\n"
                    f"QUESTION:\n{query}\n\nCONTEXT:\n{context}\n"
                )
                try:
                    rag_answer = llm.invoke(prompt)
                except Exception as e:
                    rag_answer = f"Ollama error: {e}"

    return {"status": "ok", "results": results, "rag_answer": rag_answer}
