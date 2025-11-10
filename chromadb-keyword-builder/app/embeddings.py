import os
import requests
from typing import List

_BACKEND = os.getenv("EMBEDDING_BACKEND", "st").lower()
_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "ollama")
_OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")

_model_instance = None

def _ensure_st_model():
    global _model_instance
    if _model_instance is None:
        from sentence_transformers import SentenceTransformer
        _model_instance = SentenceTransformer(_MODEL)
    return _model_instance

def encode_texts(texts: List[str], normalize: bool = True) -> List[List[float]]:
    if _BACKEND == "ollama":
        vectors = []
        for t in texts:
            resp = requests.post(f"http://{_OLLAMA_HOST}:{_OLLAMA_PORT}/api/embeddings",
                                 json={"model": _MODEL, "prompt": t}, timeout=60)
            resp.raise_for_status()
            vectors.append(resp.json()["embedding"])
        return vectors
    else:
        model = _ensure_st_model()
        vecs = model.encode(texts, normalize_embeddings=normalize)
        return vecs.tolist() if hasattr(vecs, "tolist") else vecs
