import os
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from chromadb import HttpClient
from sentence_transformers import SentenceTransformer
from keywords_loader import load_keywords

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "keywords")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
LOAD_ON_STARTUP = os.getenv("LOAD_ON_STARTUP", "true").lower() == "true"
DEFAULT_TOP_K = int(os.getenv("TOP_K", "10"))

DATA_PATH = Path(__file__).parent / "data" / "keywords.json"

app = FastAPI(title="Keyword Finder")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

client = HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
model = SentenceTransformer(EMBEDDING_MODEL)
collection = client.get_or_create_collection(COLLECTION_NAME)

@app.on_event("startup")
def startup_ingest():
    if LOAD_ON_STARTUP:
        try:
            loaded = load_keywords(client, model, COLLECTION_NAME, DATA_PATH)
            print(f"[startup] Loaded {loaded} keywords.")
        except Exception as e:
            print(f"[startup] Failed to load keywords: {e}")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ingest")
def ingest():
    try:
        loaded = load_keywords(client, model, COLLECTION_NAME, DATA_PATH)
        return {"status": "ok", "loaded": loaded}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

@app.post("/analyze")
def analyze(payload: Dict[str, Any] = Body(...), top_k: Optional[int] = None):
    text = (payload or {}).get("text", "").strip()
    if not text:
        return {"matches": []}

    k = top_k or DEFAULT_TOP_K
    query_vec = model.encode([text], normalize_embeddings=True).tolist()
    res = collection.query(query_embeddings=query_vec, n_results=k)

    matches = []
    ids = (res.get("ids") or [[]])[0]
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]
    for i in range(len(ids)):
        dist = dists[i] if i < len(dists) else None
        score = 1.0 / (1.0 + float(dist)) if dist is not None else None
        matches.append({
            "id": ids[i],
            "document": docs[i],
            "metadata": metas[i],
            "distance": dist,
            "score": score
        })

    matches.sort(key=lambda x: x.get("score") or 0, reverse=True)
    return {"matches": matches}
