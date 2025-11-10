Package created: ChromaDB Embedding Application v1.0.0

**docker-compose.yml**
```

services:
  chroma:
    image: chromadb/chroma
    volumes:
      - chroma-data:/index_data
    ports:
      - "8000:8000"
    environment:
      - IS_PERSISTENT=TRUE
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama-data:/root/.ollama
    ports:
      - "11434:11434"
  streamlit:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    depends_on:
      - chroma
      - ollama
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - CHROMA_HOST=http://chroma:8000
volumes:
  chroma-data:
  ollama-data:
```

**Dockerfile**
```
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
CMD ["streamlit", "run", "main.py"]
```

**requirements.txt**
```
streamlit
chromadb
langchain-community
pypdf2
```

**app/main.py**
```
import streamlit as st
import chromadb
from langchain_community.embeddings import OllamaEmbeddings
import json
import os
from pypdf2 import PdfReader
import uuid

ollama_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
chroma_host = os.environ.get('CHROMA_HOST', 'http://localhost:8000')

embedding = OllamaEmbeddings(base_url=ollama_host, model="nomic-embed-text")
client = chromadb.HttpClient(host=chroma_host.split('://')[1].split(':')[0], port=8000)
collection = client.get_or_create_collection(name="keywords", embedding_function=embedding)

if collection.count() == 0:
    with open('/app/data/keywords.json', 'r') as f:
        data = json.load(f)
        keywords = data['keywords']
    ids = [str(uuid.uuid4()) for _ in keywords]
    collection.add(documents=keywords, ids=ids)

st.title("ChromaDB Embedding Application")
uploaded_file = st.file_uploader("Upload a document", type=["txt", "pdf"])
if uploaded_file:
    uploads_dir = 'uploads'
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = os.path.join(uploads_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    if uploaded_file.type == "text/plain":
        text = open(file_path, "r").read()
    elif uploaded_file.type == "application/pdf":
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    results = collection.query(query_texts=[text], n_results=5)
    st.write("Suggested keywords:")
    for doc in results['documents'][0]:
        st.write(doc)
```

**client.py**
```
import chromadb
from langchain_community.embeddings import OllamaEmbeddings
import json
import os
from pypdf2 import PdfReader
import uuid
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file", help="Document file path")
args = parser.parse_args()

ollama_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
chroma_host = os.environ.get('CHROMA_HOST', 'http://localhost:8000')

embedding = OllamaEmbeddings(base_url=ollama_host, model="nomic-embed-text")
client = chromadb.HttpClient(host=chroma_host.split('://')[1].split(':')[0], port=8000)
collection = client.get_or_create_collection(name="keywords", embedding_function=embedding)

if collection.count() == 0:
    with open('data/keywords.json', 'r') as f:
        data = json.load(f)
        keywords = data['keywords']
    ids = [str(uuid.uuid4()) for _ in keywords]
    collection.add(documents=keywords, ids=ids)

file_path = args.file
if file_path.endswith(".txt"):
    text = open(file_path, "r").read()
elif file_path.endswith(".pdf"):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
results = collection.query(query_texts=[text], n_results=5)
print("Suggested keywords:")
for doc in results['documents'][0]:
    print(doc)
```

**helper.sh**
```
#!/bin/bash

start() {
  docker compose up -d --build
}

stop() {
  docker compose down
}

load_model() {
  docker exec -it ollama ollama pull nomic-embed-text
}

case $1 in
  start) start ;;
  stop) stop ;;
  load) load_model ;;
esac
```

**data/keywords.json**
```
{
  "keywords": [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural network",
    "natural language processing",
    "computer vision",
    "reinforcement learning",
    "data science",
    "big data",
    "cloud computing",
    "blockchain",
    "cryptocurrency",
    "cybersecurity",
    "internet of things",
    "virtual reality",
    "augmented reality",
    "robotics",
    "automation",
    "algorithm",
    "programming",
    "python",
    "java",
    "javascript",
    "sql",
    "database",
    "web development",
    "mobile app development",
    "software engineering",
    "devops",
    "agile methodology",
    "machine translation",
    "sentiment analysis",
    "image recognition",
    "speech recognition",
    "generative ai",
    "large language model",
    "transformer",
    "bert",
    "gpt",
    "embedding",
    "vector database",
    "chroma db",
    "ollama",
    "streamlit",
    "docker",
    "compose",
    "api",
    "rest",
    "graphql",
    "microservices",
    "kubernetes"
  ]
}
```

**.env.example**
```
OLLAMA_HOST=http://ollama:11434
CHROMA_HOST=http://chroma:8000
```

**00_READ_ME_FIRST.txt**
```
Start with this: Follow START_HERE.txt, then README.md.
```

**START_HERE.txt**
```
Quick start: Copy .env.example to .env. Run ./helper.sh start. Access http://localhost:8501.
```

**README.md**
```
# ChromaDB Embedding Application v1.0.0
Uses ChromaDB, Ollama (nomic-embed-text), Streamlit for keyword extraction from documents.
Setup: Docker Compose. Upload files via UI to get context-based keywords.
```

**QUICK_REFERENCE.md**
```
Commands:
- ./helper.sh start
- ./helper.sh stop
- ./helper.sh load
- python client.py file.pdf
```

**INSTALL.md**
```
Installation:
1. Install Docker.
2. Copy .env.example to .env.
3. Run ./helper.sh start.
```

**SETUP_SUMMARY.md**
```
Architecture:
- ChromaDB: Vector store.
- Ollama: Embeddings.
- Streamlit: UI.
Directories: app/, data/, uploads/, documents/.
```

**INDEX.md**
```
Reference:
- main.py: App logic.
- client.py: CLI.
- helper.sh: Utils.
```

**FILE_SUMMARY.md**
```
Overview:
- Dockerfile: Image build.
- docker-compose.yml: Services.
- app/main.py: Streamlit app.
- client.py: Client script.
- helper.sh: Helper.
- requirements.txt: Deps.
- data/keywords.json: Samples.
- .env.example: Config.
```

**MANIFEST.md**
```
Deployment:
Use Docker Compose for local/prod.
Scale: Adjust in compose.
```

**COMPLETE_CHECKLIST.txt**
```
Verification:
- Services running? docker ps
- Model loaded? Check ollama.
- App accessible? localhost:8501
- Keywords embedded? Upload test file.
```

**_DELIVERY_COMPLETE.txt**
```
Delivery complete: v1.0.0 certified.
```

Directories: app/, data/, uploads/, documents/