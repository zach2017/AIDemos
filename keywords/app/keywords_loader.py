import json
from pathlib import Path
from typing import List, Dict

from chromadb import HttpClient
from sentence_transformers import SentenceTransformer

def build_keyword_text(item: Dict) -> str:
    term = item.get("term", "")
    synonyms = item.get("synonyms", []) or []
    text = f"{term}. Synonyms: {', '.join(synonyms)}." if synonyms else term
    return text

def load_keywords(client: HttpClient, model: SentenceTransformer, collection_name: str, data_path: Path) -> int:
    with data_path.open("r", encoding="utf-8") as f:
        items: List[Dict] = json.load(f)

    collection = client.get_or_create_collection(collection_name)
    ids, documents, metadatas = [], [], []

    for item in items:
        ids.append(item["id"])
        documents.append(build_keyword_text(item))
        metadatas.append({
            "term": item.get("term"),
            "category": item.get("category", ""),
            "synonyms": item.get("synonyms", []),
        })

    embeddings = model.encode(documents, normalize_embeddings=True).tolist()

    try:
        collection.delete(ids=ids)
    except Exception:
        pass

    collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    return len(ids)
