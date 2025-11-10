import chromadb
import os
import glob

# --- Configuration ---
# These are the *internal* Docker service names
CHROMA_HOST = 'chroma'
CHROMA_PORT = 8000
COLLECTION_NAME = 'test_collection'
DATA_PATH = 'data/*.txt' # Path to our data inside the container

print("--- Starting Ingestion Script ---")

try:
    # 1. Connect to ChromaDB
    # We use the host 'chroma' because we are running *inside*
    # the Docker network.
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    print(f"Successfully connected to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}")

    # 2. Get or create the collection
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    print(f"Got/Created collection: '{COLLECTION_NAME}'")

    # 3. Find and process all .txt files in the data directory
    file_paths = glob.glob(DATA_PATH)
    if not file_paths:
        print(f"No files found at '{DATA_PATH}'. Exiting.")
        exit()

    print(f"Found {len(file_paths)} files to ingest.")
    
    doc_list = []
    id_list = []

    for file_path in file_paths:
        print(f"Reading file: {file_path}...")
        
        # Use the filename as the document ID
        doc_id = os.path.basename(file_path)
        
        with open(file_path, 'r') as f:
            doc_content = f.read()
            
            doc_list.append(doc_content)
            id_list.append(doc_id)
            print(f"  - Added document with ID: {doc_id}")

    # 4. Add all documents to the collection in one batch
    if doc_list:
        collection.add(
            documents=doc_list,
            ids=id_list
        )
        print(f"\nSuccessfully added {len(doc_list)} documents to '{COLLECTION_NAME}'.")
    
    print("--- Ingestion Complete ---")

except Exception as e:
    print(f"\n--- An Error Occurred ---")
    print(f"Error: {e}")
    print("Please ensure the 'chroma' service is running and accessible.")