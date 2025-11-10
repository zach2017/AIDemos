import streamlit as st
import os
import requests
import chromadb
import time

# Read connection details from environment variables
CHROMA_HOST = os.getenv('CHROMA_HOST', 'localhost')
CHROMA_PORT = int(os.getenv('CHROMA_PORT', 8000))
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost')
OLLAMA_PORT = int(os.getenv('OLLAMA_PORT', 11434))

OLLAMA_API_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags"
CHROMA_API_URL = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v1/heartbeat"

st.set_page_config(layout="wide")
st.title("Iceberg WebApp Service Status")

st.header("Service Connection Tests")
st.write("This app tests the connection to its backend services (ChromaDB and Ollama).")

# --- ChromaDB Test ---
st.subheader("ChromaDB Connection")
chroma_status = st.empty()
chroma_details = st.empty()

with chroma_status:
    st.write(f"Attempting to connect to ChromaDB at `{CHROMA_HOST}:{CHROMA_PORT}`...")

try:
    # Test HTTP connection to heartbeat
    response = requests.get(CHROMA_API_URL, timeout=5)
    response.raise_for_status() # Raise exception for bad status codes
    chroma_status.success(f"Successfully connected to ChromaDB heartbeat API (HTTP GET `{CHROMA_API_URL}`).")
    chroma_details.json(response.json())

    # Test client connection
    st.write("Attempting to connect with `chromadb.HttpClient`...")
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    heartbeat = client.heartbeat()
    st.write("`HttpClient.heartbeat()` response:")
    st.json(heartbeat)
    st.success("ChromaDB client connection successful!")

except Exception as e:
    chroma_status.error(f"Failed to connect to ChromaDB.")
    chroma_details.exception(e)

# --- Ollama Test ---
st.subheader("Ollama Connection")
ollama_status = st.empty()
ollama_details = st.empty()

with ollama_status:
    st.write(f"Attempting to connect to Ollama at `{OLLAMA_HOST}:{OLLAMA_PORT}`...")

try:
    # Ollama can be slow to start, so we give it a moment
    time.sleep(3) 
    response = requests.get(OLLAMA_API_URL, timeout=10)
    response.raise_for_status()
    ollama_status.success(f"Successfully connected to Ollama API (HTTP GET `{OLLAMA_API_URL}`).")
    st.write("Available Ollama models (will be empty on first run):")
    ollama_details.json(response.json())

except Exception as e:
    ollama_status.error(f"Failed to connect to Ollama.")
    ollama_details.exception(e)

st.header("Environment Variables")
st.json({
    "CHROMA_HOST": CHROMA_HOST,
    "CHROMA_PORT": CHROMA_PORT,
    "OLLAMA_HOST": OLLAMA_HOST,
    "OLLAMA_PORT": OLLAMA_PORT,
})