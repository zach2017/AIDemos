# 🌐 Web Application User Guide

## Overview

The Apache Iceberg + RAG Demo includes a beautiful web interface built with Streamlit. This guide will help you get the most out of the web application.

---

## 🚀 Quick Start

### 1. Start the Demo
```bash
# Start all services
docker-compose up -d

# Initialize data (required first time)
docker exec -it iceberg-app python /app/scripts/demo.py

# Open web app
make webapp
# OR visit: http://localhost:8501
```

### 2. First Time Setup

The web app will be available at `http://localhost:8501` immediately after starting services, but you need to run the demo script first to populate data.

**Status Indicators:**
- ✅ Green = Service connected and working
- ❌ Red = Service not responding
- Check the sidebar for system status

---

## 📖 Features Overview

The web app has 4 main tabs:

### 🔍 Tab 1: Smart Search
**Purpose:** Ask questions and get AI-powered answers using RAG

**Features:**
- Natural language question input
- Sample questions to get started
- Configurable number of results (1-10)
- Real-time processing status
- Retrieved products with similarity scores
- AI-generated answers
- View context sent to LLM

**How to Use:**
1. Type your question or select a sample
2. Adjust number of results (default: 3)
3. Click "🔍 Search"
4. Watch the RAG process unfold
5. Review retrieved products
6. Read the AI-generated answer
7. Expand "View Context" to see what the LLM received

**Example Questions:**
- "What laptops do you have for developers?"
- "Show me furniture for home office under $500"
- "I need ergonomic accessories"
- "What's the cheapest product in stock?"
- "Compare laptop and keyboard prices"

**Tips:**
- More results = more context but slower processing
- Similarity score shows relevance (higher = better match)
- Context box shows exactly what the LLM sees

---

### 📦 Tab 2: Product Catalog
**Purpose:** Browse and filter all products in the database

**Features:**
- Complete product listing
- Category filtering
- Price range slider
- Multiple sorting options
- Summary statistics
- Product count by category

**How to Use:**
1. Use filters to narrow down products:
   - **Category:** Select specific category or "All"
   - **Price Range:** Drag slider to set min/max
   - **Sort By:** Choose sorting method

2. View products in organized list format
   - Name and category
   - Price and stock levels
   - Click 🔍 to see product ID

3. Check summary statistics at bottom:
   - Total products shown
   - Average price
   - Total stock
   - Number of categories

**Sorting Options:**
- **Name:** Alphabetical order
- **Price (Low-High):** Cheapest first
- **Price (High-Low):** Most expensive first
- **Stock:** Highest stock first

**Use Cases:**
- Find products in a price range
- Check stock levels
- Compare category sizes
- Get overall inventory view

---

### 🧪 Tab 3: RAG Process
**Purpose:** Learn how RAG works and understand the system

**Features:**
- Side-by-side comparison (With RAG vs Without RAG)
- Interactive embedding generator
- Step-by-step process visualization
- Key concepts explanation
- Benefits and use cases

**How to Use:**

**1. Compare Approaches**
- Left side: Traditional LLM (may hallucinate)
- Right side: RAG approach (grounded in facts)
- Understand the difference visually

**2. Try Embedding Generation**
- Enter any text
- Click "Generate Embedding"
- See the vector representation
- Understand how text becomes numbers

**3. Learn Key Concepts**
- Read about embeddings and vectors
- Understand semantic search
- Explore RAG benefits
- Review common use cases

**Educational Value:**
- Perfect for presentations
- Training new team members
- Understanding the technology
- Explaining RAG to stakeholders

---

### 📈 Tab 4: Analytics
**Purpose:** Visualize data and get insights

**Features:**
- Interactive charts and graphs
- Category distribution
- Price analysis
- Stock level visualization
- Detailed statistics
- Category-specific breakdowns

**Available Visualizations:**

**1. Products by Category** (Bar Chart)
- See distribution across categories
- Identify largest categories
- Quick visual comparison

**2. Price Distribution** (Line Chart)
- Understand price ranges
- Spot pricing gaps
- Analyze pricing strategy

**3. Stock Levels** (Bar Chart)
- Monitor inventory by product
- Identify low stock items
- Plan reordering

**4. Price vs Stock** (Scatter Plot)
- Correlation between price and stock
- Identify patterns
- Strategic insights

**Key Metrics:**
- Total Products
- Average Price
- Total Inventory Value
- Low Stock Items (<30 units)

**Category Breakdowns:**
- Expandable sections per category
- Products count
- Average price
- Total stock
- Detailed product table

**Use Cases:**
- Inventory management
- Pricing analysis
- Category performance
- Stock optimization

---

## 🎨 User Interface Guide

### Sidebar
**Location:** Left side of screen

**Contains:**
- Iceberg logo
- About section
- System status indicators
- Real-time metrics

**Status Checks:**
- Chroma connection (✅/❌)
- Ollama connection (✅/❌)
- Number of collections
- Number of models loaded

### Main Area
**Layout:** Wide, centered content

**Features:**
- Tab navigation at top
- Content area below
- Responsive design
- Clear visual hierarchy

### Color Coding
- 🔵 Blue: Primary actions and headers
- 🟢 Green: Success states
- 🟡 Yellow: Context and information
- 🔴 Red: Errors or warnings
- ⚪ White/Gray: Background and cards

---

## 💡 Pro Tips

### For Best Results:

1. **Be Specific in Questions**
   - Bad: "Show me products"
   - Good: "What laptops are good for software development?"

2. **Use Natural Language**
   - The system understands conversational questions
   - Don't worry about exact keywords

3. **Adjust Result Count**
   - More results = more context for LLM
   - But slower processing time
   - 3-5 results is usually optimal

4. **Check Similarity Scores**
   - Above 0.8 = Very relevant
   - 0.6-0.8 = Moderately relevant
   - Below 0.6 = May not be relevant

5. **Review Retrieved Context**
   - Always check what context the LLM received
   - Helps understand the answer
   - Validates accuracy

### Troubleshooting:

**Web App Won't Load**
```bash
# Check if container is running
docker ps | grep webapp

# Check logs
docker-compose logs webapp

# Restart the service
docker-compose restart webapp
```

**No Products Found**
```bash
# Run the demo to populate data
docker exec -it iceberg-app python /app/scripts/demo.py
```

**Services Show Disconnected**
```bash
# Check all services
docker-compose ps

# Restart failed services
docker-compose restart chroma ollama

# Wait a minute and refresh browser
```

**Slow Response Times**
- First query after starting is slow (model loading)
- Reduce number of results
- Check system resources (RAM, CPU)
- Ollama needs time to generate responses

---

## 🔧 Customization

### Modify Sample Questions

Edit `app/streamlit_app.py`, find:
```python
sample_questions = [
    "Your custom question here",
    # Add more...
]
```

### Change Number of Results Default

In `app/streamlit_app.py`:
```python
n_results = st.slider("Number of products to retrieve:", 1, 10, 5)  # Changed default to 5
```

### Add Custom Styling

CSS is in the `st.markdown()` section at the top of `streamlit_app.py`. Modify colors, fonts, layouts as needed.

### Change Port

In `docker-compose.yml`:
```yaml
ports:
  - "8080:8501"  # Change 8080 to your preferred port
```

---

## 📊 Use Cases

### 1. Customer Demos
- Show RAG in action
- Impress stakeholders
- Live product search
- Analytics dashboard

### 2. Training
- Teach team about RAG
- Interactive learning
- Visual process explanation
- Hands-on experience

### 3. Development
- Test queries quickly
- Validate search results
- Monitor system status
- Iterate on prompts

### 4. Presentations
- Professional interface
- Real-time demonstrations
- Clear visualizations
- Impressive analytics

---

## 🎓 Learning Path

### Beginner (15 minutes)
1. Open web app
2. Try sample questions in Smart Search
3. Browse Product Catalog
4. Review RAG Process comparison

### Intermediate (30 minutes)
1. Ask custom questions
2. Adjust result counts
3. Review retrieved context
4. Explore analytics
5. Check category breakdowns

### Advanced (1 hour)
1. Generate custom embeddings
2. Analyze similarity scores
3. Compare different query types
4. Study analytics patterns
5. Customize the interface

---

## 🚀 Performance Tips

### For Faster Queries:
1. **Reduce Results:** 3 instead of 10
2. **Specific Questions:** More focused = faster
3. **Keep Ollama Warm:** First query is slow, subsequent are fast
4. **Adequate Resources:** Ensure Docker has 8GB+ RAM

### For Better Answers:
1. **Increase Results:** 5-7 for complex questions
2. **Be Specific:** "laptop for Python development" vs "laptop"
3. **Review Context:** Check if relevant products were retrieved
4. **Iterate:** Refine questions based on results

---

## 🎉 Quick Reference

```
┌─────────────────────────────────────────────────┐
│              Web App Quick Reference            │
├─────────────────────────────────────────────────┤
│                                                 │
│  URL:        http://localhost:8501              │
│  Open:       make webapp                        │
│  Restart:    docker-compose restart webapp      │
│  Logs:       docker-compose logs -f webapp      │
│                                                 │
│  Tabs:                                          │
│    🔍 Smart Search    - Ask questions           │
│    📦 Product Catalog - Browse products         │
│    🧪 RAG Process     - Learn how it works      │
│    📈 Analytics       - View insights           │
│                                                 │
│  Status Check:                                  │
│    Sidebar shows connection status              │
│    ✅ = Working    ❌ = Problem                │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📞 Support

**Not Working?**
1. Check [QUICKSTART.md](QUICKSTART.md) - Basic setup
2. Check [README.md](README.md) - Troubleshooting section
3. Run `make health` - System status
4. Check logs - `docker-compose logs webapp`

**Want to Learn More?**
1. [TUTORIAL.md](TUTORIAL.md) - Complete explanation
2. [CHEATSHEET.md](CHEATSHEET.md) - Quick concepts
3. [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details

---

**Enjoy the web app! 🎉**

For the best experience:
1. ✅ Run the demo first (`make demo`)
2. ✅ Wait for all services to be healthy
3. ✅ Open in a modern browser (Chrome, Firefox, Safari)
4. ✅ Explore all four tabs
5. ✅ Try custom questions

Happy exploring! 🚀
