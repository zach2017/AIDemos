import os
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentLoader:
    """Handles loading and splitting documents."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def load_document(self, file_path: str) -> List[Dict[str, str]]:
        """Load a single document and split it into chunks."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(content)
        
        # Create document objects
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                'content': chunk,
                'metadata': {
                    'source': os.path.basename(file_path),
                    'chunk_id': i
                }
            })
        
        return documents
    
    def load_directory(self, directory_path: str) -> List[Dict[str, str]]:
        """Load all text files from a directory."""
        documents = []
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        for filename in os.listdir(directory_path):
            if filename.endswith(('.txt', '.md')):
                file_path = os.path.join(directory_path, filename)
                try:
                    docs = self.load_document(file_path)
                    documents.extend(docs)
                except Exception as e:
                    print(f"Error loading {filename}: {str(e)}")
        
        return documents
