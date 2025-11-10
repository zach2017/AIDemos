#!/usr/bin/env python3
"""
Streamlit Web App for Apache Iceberg + RAG Demo
"""

import streamlit as st
import chromadb
import requests
import pandas as pd
from datetime import datetime
import time

# Configuration
CHROMA_HOST = "chroma"
CHROMA_PORT = 8000
OLLAMA_BASE_URL = "http://ollama:11434"

# Page configuration
st.set_page_config(
    page_title="Apache Iceberg + RAG Demo",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .product-card {
        background: #f8f9fa;
        border-left: 4px solid #1E88E5;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .context-box {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .answer-box {
        background: #d1ecf1;
        border: 1px solid #17a2b8;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .process-step {
        background: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_chroma_client():
    """Initialize Chroma client"""
    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, 
                                     port=CHROMA_PORT,tenant="default_tenant",
                                     database="default_database"
                                     )
        return client
    
    except Exception as e:
        st.error(f"Failed to connect to Chroma: {e}")
        return None


def generate_embeddings(text):
    """Generate embeddings using Ollama"""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": text
            },
            timeout=30
        )
        return response.json()['embedding']
    except Exception as e:
        st.error(f"Failed to generate embeddings: {e}")
        return None


def query_ollama(prompt, model="llama3.2:1b"):
    """Query Ollama LLM"""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        return response.json()['response']
    except Exception as e:
        st.error(f"Failed to query Ollama: {e}")
        return None


def search_products(collection, query_text, n_results=5):
    """Search for similar products"""
    try:
        query_embedding = generate_embeddings(query_text)
        if query_embedding is None:
            return None
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results
    except Exception as e:
        st.error(f"Search failed: {e}")
        return None


def main():
    # Header
    st.markdown('<div class="main-header">🧊 Apache Iceberg + RAG Demo</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent Product Search with Retrieval Augmented Generation</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://iceberg.apache.org/img/Iceberg-logo.png", width=200)
        st.markdown("## About This Demo")
        st.info("""
        This demo showcases:
        - **Apache Iceberg** for data lake management
        - **Chroma** for vector search
        - **Ollama** for local AI
        - **RAG** to reduce hallucinations
        """)
        
        st.markdown("---")
        st.markdown("### System Status")
        
        # Check system status
        try:
            client = get_chroma_client()
            if client:
                collections = client.list_collections()
                st.success("✅ Chroma Connected")
                st.metric("Collections", len(collections))
            else:
                st.error("❌ Chroma Disconnected")
        except:
            st.error("❌ System Error")
        
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                st.success("✅ Ollama Connected")
                models = response.json().get('models', [])
                st.metric("Models Loaded", len(models))
            else:
                st.error("❌ Ollama Disconnected")
        except:
            st.error("❌ Ollama Error")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Smart Search", "📊 Product Catalog", "🧪 RAG Process", "📈 Analytics"])
    
    # Tab 1: Smart Search
    with tab1:
        st.markdown("## Ask Questions About Products")
        st.markdown("Using RAG (Retrieval Augmented Generation) to provide accurate, grounded answers.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Sample questions
            st.markdown("### Try These Questions:")
            sample_questions = [
                "What laptops do you have for developers?",
                "Show me furniture for home office under $500",
                "I need ergonomic accessories",
                "What's the cheapest product in stock?",
                "Compare laptop and keyboard prices"
            ]
            
            selected_question = st.selectbox("Or select a sample:", [""] + sample_questions)
            
            question = st.text_input(
                "Your Question:",
                value=selected_question,
                placeholder="Ask anything about our products..."
            )
            
            n_results = st.slider("Number of products to retrieve:", 1, 10, 3)
            
            search_button = st.button("🔍 Search", type="primary", use_container_width=True)
        
        with col2:
            st.markdown("### How It Works")
            st.markdown("""
            1. 📝 Convert question to vector
            2. 🔎 Search similar products
            3. 📦 Retrieve product details
            4. 🤖 Generate AI answer
            5. ✅ Return grounded response
            """)
        
        if search_button and question:
            with st.spinner("Searching..."):
                client = get_chroma_client()
                if client:
                    try:
                        collection = client.get_collection(name="products")
                        
                        # Show process
                        st.markdown("---")
                        st.markdown("### 🔄 RAG Process")
                        
                        # Step 1: Vectorize
                        with st.status("Processing your question...", expanded=True) as status:
                            st.write("Step 1: Converting question to vector embedding...")
                            time.sleep(0.5)
                            
                            query_embedding = generate_embeddings(question)
                            if query_embedding:
                                st.write(f"✅ Generated {len(query_embedding)}-dimensional vector")
                            
                            st.write("Step 2: Searching vector database...")
                            time.sleep(0.5)
                            
                            results = collection.query(
                                query_embeddings=[query_embedding],
                                n_results=n_results
                            )
                            
                            st.write(f"✅ Found {len(results['documents'][0])} relevant products")
                            
                            st.write("Step 3: Retrieving product details...")
                            time.sleep(0.5)
                            st.write("✅ Retrieved full context")
                            
                            status.update(label="✅ Processing complete!", state="complete")
                        
                        # Display results
                        st.markdown("### 📦 Retrieved Products")
                        
                        context_docs = []
                        for i, (doc, metadata, distance) in enumerate(zip(
                            results['documents'][0],
                            results['metadatas'][0],
                            results['distances'][0]
                        )):
                            similarity = 1 - distance
                            
                            st.markdown(f"""
                            <div class="product-card">
                                <h4>{i+1}. {metadata['name']}</h4>
                                <p><strong>Category:</strong> {metadata['category']} | 
                                   <strong>Price:</strong> ${metadata['price']} | 
                                   <strong>Stock:</strong> {metadata['stock']}</p>
                                <p><strong>Similarity:</strong> {similarity:.2%}</p>
                                <p style="font-size: 0.9em; color: #666;">{doc}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            context_docs.append(doc)
                        
                        # Generate answer
                        st.markdown("### 🤖 AI-Generated Answer")
                        
                        with st.spinner("Generating answer..."):
                            context = "\n\n".join(context_docs)
                            
                            prompt = f"""Based on the following product information, provide a helpful and detailed answer to the user's question.

Product Information:
{context}

User Question: {question}

Provide a clear, concise answer focusing on the most relevant products. Include specific details like prices and features."""
                            
                            answer = query_ollama(prompt)
                            
                            if answer:
                                st.markdown(f"""
                                <div class="answer-box">
                                    <h4>💡 Answer:</h4>
                                    <p>{answer}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Show context used
                            with st.expander("📋 View Context Sent to LLM"):
                                st.markdown(f"""
                                <div class="context-box">
                                    <strong>Context:</strong><br>
                                    {context.replace(chr(10), '<br>')}
                                </div>
                                """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.info("💡 Make sure to run the demo first: `make demo`")
    
    # Tab 2: Product Catalog
    with tab2:
        st.markdown("## 📦 Product Catalog")
        st.markdown("Browse all products stored in the Chroma vector database.")
        
        client = get_chroma_client()
        if client:
            try:
                collection = client.get_collection(name="products")
                
                # Get all products
                results = collection.get()
                
                if results['metadatas']:
                    st.success(f"Total Products: {len(results['metadatas'])}")
                    
                    # Create DataFrame
                    df = pd.DataFrame(results['metadatas'])
                    
                    # Filters
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        categories = ['All'] + sorted(df['category'].unique().tolist())
                        selected_category = st.selectbox("Category:", categories)
                    
                    with col2:
                        min_price = float(df['price'].min())
                        max_price = float(df['price'].max())
                        price_range = st.slider(
                            "Price Range:",
                            min_price,
                            max_price,
                            (min_price, max_price)
                        )
                    
                    with col3:
                        sort_by = st.selectbox("Sort By:", ["Name", "Price (Low-High)", "Price (High-Low)", "Stock"])
                    
                    # Filter data
                    filtered_df = df.copy()
                    if selected_category != 'All':
                        filtered_df = filtered_df[filtered_df['category'] == selected_category]
                    
                    filtered_df = filtered_df[
                        (filtered_df['price'] >= price_range[0]) &
                        (filtered_df['price'] <= price_range[1])
                    ]
                    
                    # Sort data
                    if sort_by == "Name":
                        filtered_df = filtered_df.sort_values('name')
                    elif sort_by == "Price (Low-High)":
                        filtered_df = filtered_df.sort_values('price')
                    elif sort_by == "Price (High-Low)":
                        filtered_df = filtered_df.sort_values('price', ascending=False)
                    elif sort_by == "Stock":
                        filtered_df = filtered_df.sort_values('stock', ascending=False)
                    
                    # Display products
                    st.markdown(f"### Showing {len(filtered_df)} products")
                    
                    for idx, row in filtered_df.iterrows():
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{row['name']}**")
                            st.caption(row['category'])
                        
                        with col2:
                            st.metric("Price", f"${row['price']}")
                        
                        with col3:
                            st.metric("Stock", row['stock'])
                        
                        with col4:
                            if st.button("🔍", key=f"view_{idx}"):
                                st.info(f"Product ID: {row['product_id']}")
                        
                        st.divider()
                    
                    # Summary statistics
                    st.markdown("### 📊 Summary Statistics")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Products", len(filtered_df))
                    
                    with col2:
                        st.metric("Avg Price", f"${filtered_df['price'].mean():.2f}")
                    
                    with col3:
                        st.metric("Total Stock", int(filtered_df['stock'].sum()))
                    
                    with col4:
                        st.metric("Categories", filtered_df['category'].nunique())
                
                else:
                    st.warning("No products found. Run the demo first: `make demo`")
            
            except Exception as e:
                st.error(f"Error loading products: {e}")
                st.info("💡 Run the demo first: `make demo`")
    
    # Tab 3: RAG Process Visualization
    with tab3:
        st.markdown("## 🧪 Understanding the RAG Process")
        st.markdown("Learn how Retrieval Augmented Generation works step-by-step.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Without RAG ❌")
            st.markdown("""
            <div class="process-step">
                <strong>1. User asks question</strong><br>
                "What laptops do you have?"
            </div>
            <div class="process-step">
                <strong>2. LLM generates answer from training data</strong><br>
                ⚠️ May hallucinate<br>
                ⚠️ No access to your data<br>
                ⚠️ Can't cite sources
            </div>
            <div class="process-step">
                <strong>3. Returns potentially wrong answer</strong><br>
                "We have the X200 for $899" ❌<br>
                (Product doesn't exist or wrong price)
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### With RAG ✅")
            st.markdown("""
            <div class="process-step">
                <strong>1. User asks question</strong><br>
                "What laptops do you have?"
            </div>
            <div class="process-step">
                <strong>2. Convert to vector & search</strong><br>
                ✅ Finds relevant products<br>
                ✅ Based on semantic similarity
            </div>
            <div class="process-step">
                <strong>3. Retrieve actual data</strong><br>
                Laptop Pro 15 - $1,299.99<br>
                (Real product from database)
            </div>
            <div class="process-step">
                <strong>4. LLM generates answer with context</strong><br>
                ✅ Grounded in facts<br>
                ✅ Can cite sources
            </div>
            <div class="process-step">
                <strong>5. Returns accurate answer</strong><br>
                "We have the Laptop Pro 15 for $1,299.99" ✅<br>
                (Factually correct, verifiable)
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Interactive demo
        st.markdown("### 🎮 Try It Yourself")
        
        demo_text = st.text_input(
            "Enter product description:",
            "High-performance laptop for developers"
        )
        
        if st.button("Generate Embedding", use_container_width=True):
            with st.spinner("Generating..."):
                embedding = generate_embeddings(demo_text)
                
                if embedding:
                    st.success(f"Generated {len(embedding)}-dimensional embedding vector")
                    
                    # Show first 10 dimensions
                    st.markdown("**First 10 dimensions:**")
                    st.code(embedding[:10])
                    
                    st.info("""
                    💡 This vector represents the semantic meaning of your text.
                    Similar texts will have similar vectors, allowing semantic search!
                    """)
        
        # Explanation
        st.markdown("---")
        st.markdown("### 📚 Key Concepts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Embeddings (Vectors)**
            - Text → Numbers
            - Captures semantic meaning
            - 768 dimensions (nomic-embed-text)
            - Similar texts = Similar vectors
            
            **Vector Search**
            - Compare vectors mathematically
            - Find most similar items
            - O(log n) with HNSW index
            - Much faster than scanning all data
            """)
        
        with col2:
            st.markdown("""
            **RAG Benefits**
            - ✅ Reduces hallucinations
            - ✅ Access to current data
            - ✅ Citable sources
            - ✅ Domain-specific knowledge
            - ✅ No retraining needed
            
            **Use Cases**
            - Customer support
            - Product search
            - Document Q&A
            - Knowledge bases
            """)
    
    # Tab 4: Analytics
    with tab4:
        st.markdown("## 📈 System Analytics")
        
        client = get_chroma_client()
        if client:
            try:
                collection = client.get_collection(name="products")
                results = collection.get()
                
                if results['metadatas']:
                    df = pd.DataFrame(results['metadatas'])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Products by Category")
                        category_counts = df['category'].value_counts()
                        st.bar_chart(category_counts)
                        
                        st.markdown("### Price Distribution")
                        st.line_chart(df['price'].sort_values())
                    
                    with col2:
                        st.markdown("### Stock Levels")
                        stock_data = df[['name', 'stock']].set_index('name')
                        st.bar_chart(stock_data)
                        
                        st.markdown("### Price vs Stock")
                        scatter_data = df[['price', 'stock']]
                        st.scatter_chart(scatter_data)
                    
                    # Detailed stats
                    st.markdown("---")
                    st.markdown("### 📊 Detailed Statistics")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Total Products",
                            len(df),
                            help="Number of products in catalog"
                        )
                    
                    with col2:
                        st.metric(
                            "Avg Price",
                            f"${df['price'].mean():.2f}",
                            help="Average product price"
                        )
                    
                    with col3:
                        st.metric(
                            "Total Inventory Value",
                            f"${(df['price'] * df['stock']).sum():,.2f}",
                            help="Sum of all stock values"
                        )
                    
                    with col4:
                        st.metric(
                            "Low Stock Items",
                            len(df[df['stock'] < 30]),
                            help="Products with stock < 30"
                        )
                    
                    # Category breakdown
                    st.markdown("### Category Breakdown")
                    for category in df['category'].unique():
                        cat_df = df[df['category'] == category]
                        
                        with st.expander(f"📦 {category} ({len(cat_df)} products)"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Products", len(cat_df))
                            
                            with col2:
                                st.metric("Avg Price", f"${cat_df['price'].mean():.2f}")
                            
                            with col3:
                                st.metric("Total Stock", int(cat_df['stock'].sum()))
                            
                            st.dataframe(
                                cat_df[['name', 'price', 'stock']],
                                use_container_width=True
                            )
                
            except Exception as e:
                st.error(f"Error loading analytics: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>Apache Iceberg + RAG Demo | Built with ❤️ using Streamlit</p>
        <p>🧊 Iceberg | 🔍 Chroma | 🤖 Ollama | ⚡ Spark</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
