import os
import json
import streamlit as st
from pathlib import Path
from typing import List, Dict

from chromadb import HttpClient
from keywords_loader import load_keywords
from keywords_admin import add_or_update_keywords, delete_keywords

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "keywords")
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "st")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DEFAULT_TOP_K = int(os.getenv("TOP_K", "10"))

DATA_PATH = Path(__file__).parent / "data" / "keywords.json"

st.set_page_config(page_title="Chroma Keyword Builder", layout="wide")
client = HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection = client.get_or_create_collection(COLLECTION_NAME)

st.sidebar.title("Settings")
st.sidebar.write(f"**Backend**: {EMBEDDING_BACKEND}")
st.sidebar.write(f"**Model**: {EMBEDDING_MODEL}")

if st.sidebar.button("Reload from keywords.json"):
    try:
        loaded = load_keywords(client, COLLECTION_NAME, DATA_PATH)
        st.sidebar.success(f"Reloaded {loaded} keywords.")
    except Exception as e:
        st.sidebar.error(str(e))

tab_admin, tab_analyze = st.tabs(["⚙️ Keyword Builder", "🔎 Analyze Document"])

with tab_admin:
    st.header("Build & Manage Keywords")
    colL, colR = st.columns(2)
    with colL:
        st.subheader("Add / Update")
        with st.form("add_update"):
            kid = st.text_input("ID", placeholder="k11")
            term = st.text_input("Term", placeholder="data governance")
            synonyms = st.text_input("Synonyms (comma-separated)")
            category = st.text_input("Category", placeholder="data")
            submit = st.form_submit_button("Save")
        if submit:
            if not kid or not term:
                st.error("ID and Term required.")
            else:
                items = [{
                    "id": kid.strip(),
                    "term": term.strip(),
                    "synonyms": [s.strip() for s in synonyms.split(",") if s.strip()],
                    "category": category.strip() if category else ""
                }]
                try:
                    n = add_or_update_keywords(client, COLLECTION_NAME, items)
                    st.success(f"Saved {n} keyword(s).")
                except Exception as e:
                    st.error(str(e))
    with colR:
        st.subheader("Delete")
        del_ids = st.text_input("IDs (comma-separated)", placeholder="k1, k2")
        if st.button("Delete"):
            ids = [x.strip() for x in del_ids.split(",") if x.strip()]
            try:
                n = delete_keywords(client, COLLECTION_NAME, ids)
                st.success(f"Deleted {n} keyword(s).")
            except Exception as e:
                st.error(str(e))

with tab_analyze:
    st.header("Document → Related Keywords")
    top_k = st.slider("Top K", 1, 30, DEFAULT_TOP_K)
    text = st.text_area("Paste text", height=200)
    file = st.file_uploader("Or upload .txt", type=["txt"])
    if file and not text.strip():
        text = file.read().decode("utf-8")
    if st.button("Analyze"):
        if not text.strip():
            st.warning("Enter text.")
        else:
            from embeddings import encode_texts
            with st.spinner("Embedding and searching..."):
                qvec = encode_texts([text])
                res = collection.query(query_embeddings=qvec, n_results=top_k)
            ids = (res.get("ids") or [[]])[0]
            docs = (res.get("documents") or [[]])[0]
            metas = (res.get("metadatas") or [[]])[0]
            dists = (res.get("distances") or [[]])[0]
            for i in range(len(ids)):
                dist = dists[i]
                score = 1/(1+float(dist))
                m = metas[i]
                st.markdown(f"**{m.get('term')}** — Similarity: {score:.4f}  
Category: {m.get('category')}  
Synonyms: {', '.join(m.get('synonyms', []))}")
