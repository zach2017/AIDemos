from typing import Dict, List
from chromadb import HttpClient
from embeddings import encode_texts

def keyword_text(term: str, synonyms: List[str]) -> str:
    syn = ", ".join(synonyms) if synonyms else ""
    return f"{term}. Synonyms: {syn}." if syn else term

def add_or_update_keywords(client: HttpClient, collection_name: str, items: List[Dict]) -> int:
    col = client.get_or_create_collection(collection_name)
    ids, docs, metas = [], [], []
    for it in items:
        ids.append(it["id"])
        docs.append(keyword_text(it["term"], it.get("synonyms", [])))
        metas.append({
            "term": it["term"],
            "category": it.get("category", ""),
            "synonyms": it.get("synonyms", [])
        })
    try:
        col.delete(ids=ids)
    except Exception:
        pass
    vectors = encode_texts(docs)
    col.add(ids=ids, documents=docs, metadatas=metas, embeddings=vectors)
    return len(ids)

def delete_keywords(client: HttpClient, collection_name: str, ids: List[str]) -> int:
    col = client.get_or_create_collection(collection_name)
    col.delete(ids=ids)
    return len(ids)
