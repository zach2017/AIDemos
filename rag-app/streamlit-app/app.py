import streamlit as st
import os
import time

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from utils.vectorstore import VectorStoreManager
from utils.rag_chain import RAGChain

# Page configuration
st.set_page_config(
    page_title="RAG Q&A System",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'vectorstore_ready' not in st.session_state:
    st.session_state.vectorstore_ready = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for configuration and document management
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Environment settings
    st.subheader("System Status")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    chroma_host = os.getenv("CHROMA_HOST", "chromadb")
    chroma_port = os.getenv("CHROMA_PORT", "8000")
    
    st.info(f"🦙 Ollama: {ollama_url}")
    st.info(f"📊 ChromaDB: {chroma_host}:{chroma_port}")
    
    st.divider()
    
    # Document loading section
    st.subheader("📚 Document Management")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a document (TXT, MD, or PDF)",
        type=['txt', 'md', 'pdf']
    )
    
    if uploaded_file:
        if st.button("📥 Process Document"):
            with st.spinner("Processing document..."):
                try:
                    # Save uploaded file temporarily
                    temp_path = f"/app/data/temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Load and process document
                    doc_loader = DocumentLoader()
                    documents = doc_loader.load_document(temp_path)
                    
                    # Initialize vector store
                    vectorstore_manager = VectorStoreManager(
                        chroma_host=chroma_host,
                        chroma_port=chroma_port
                    )
                    vectorstore_manager.add_documents(documents)
                    
                    st.session_state.vectorstore_ready = True
                    st.success(f"✅ Processed {len(documents)} document chunks!")
                    
                    # Clean up temp file
                    os.remove(temp_path)
                    
                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
    
    # Load sample data
    if st.button("📖 Load Sample Data"):
        with st.spinner("Loading sample data..."):
            try:
                doc_loader = DocumentLoader()
                documents = doc_loader.load_directory("/app/data")
                
                vectorstore_manager = VectorStoreManager(
                    chroma_host=chroma_host,
                    chroma_port=chroma_port
                )
                vectorstore_manager.add_documents(documents)
                
                st.session_state.vectorstore_ready = True
                st.success(f"✅ Loaded {len(documents)} document chunks!")
                
            except Exception as e:
                st.error(f"Error loading sample data: {str(e)}")
    
    # Clear vector store
    if st.button("🗑️ Clear Vector Store"):
        try:
            vectorstore_manager = VectorStoreManager(
                chroma_host=chroma_host,
                chroma_port=chroma_port
            )
            vectorstore_manager.clear_collection()
            st.session_state.vectorstore_ready = False
            st.session_state.chat_history = []
            st.success("✅ Vector store cleared!")
        except Exception as e:
            st.error(f"Error clearing vector store: {str(e)}")

# Main content area
st.title("🤖 RAG Q&A System")
st.markdown("Ask questions about your documents using local AI models!")

# Check if vector store is ready
if not st.session_state.vectorstore_ready:
    st.warning("⚠️ Please load documents first using the sidebar options.")
    st.info("👈 Upload your own documents or load the sample data to get started!")
else:
    st.success("✅ System ready! Ask your questions below.")

# Chat interface
st.subheader("💬 Chat")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 View Sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"**Source {i}:**")
                    st.text(source)
                    st.divider()

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    if st.session_state.vectorstore_ready:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Initialize RAG chain
                rag_chain = RAGChain(
                    ollama_url=ollama_url,
                    chroma_host=chroma_host,
                    chroma_port=chroma_port
                )
                
                # Get response
                with st.spinner("Thinking..."):
                    response = rag_chain.query(prompt)
                
                # Display response
                message_placeholder.markdown(response["answer"])
                
                # Add assistant message to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "sources": response["sources"]
                })
                
                # Display sources
                if response["sources"]:
                    with st.expander("📚 View Sources"):
                        for i, source in enumerate(response["sources"], 1):
                            st.markdown(f"**Source {i}:**")
                            st.text(source)
                            st.divider()
                
            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })
    else:
        st.error("⚠️ Please load documents first!")

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <small>Powered by Ollama (LLaMA 2) + ChromaDB + Streamlit</small>
    </div>
""", unsafe_allow_html=True)
