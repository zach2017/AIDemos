import requests
import json
from typing import Dict, List
from .vectorstore import VectorStoreManager

class RAGChain:
    """Handles the RAG (Retrieval-Augmented Generation) workflow."""
    
    def __init__(self, ollama_url: str, chroma_host: str, chroma_port: str):
        self.ollama_url = ollama_url
        self.vectorstore = VectorStoreManager(chroma_host, chroma_port)
    
    def query(self, question: str, n_results: int = 3) -> Dict[str, any]:
        """
        Execute a RAG query:
        1. Retrieve relevant documents from vector store
        2. Generate answer using LLM with context
        """
        # Step 1: Retrieve relevant documents
        retrieval_results = self.vectorstore.query(question, n_results=n_results)
        
        if not retrieval_results['documents']:
            return {
                'answer': "I couldn't find any relevant information in the knowledge base to answer your question.",
                'sources': []
            }
        
        # Step 2: Build context from retrieved documents
        context = "\n\n".join([
            f"Document {i+1}:\n{doc}"
            for i, doc in enumerate(retrieval_results['documents'])
        ])
        
        # Step 3: Create prompt for LLM
        prompt = self._create_prompt(question, context)
        
        # Step 4: Generate answer using Ollama
        answer = self._generate_answer(prompt)
        
        return {
            'answer': answer,
            'sources': retrieval_results['documents']
        }
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create a prompt for the LLM with context."""
        return f"""You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {question}

Instructions:
- Answer the question based ONLY on the information provided in the context above.
- If the context doesn't contain enough information to answer the question, say so.
- Be concise and accurate.
- Do not make up information that is not in the context.

Answer:"""
    
    def _generate_answer(self, prompt: str) -> str:
        """Generate an answer using Ollama."""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response generated.')
            else:
                return f"Error: Unable to generate response (Status: {response.status_code})"
        
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {str(e)}"
        except Exception as e:
            return f"Error generating response: {str(e)}"
