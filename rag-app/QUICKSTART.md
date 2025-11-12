# Quick Start Guide

Get your RAG system running in 3 simple steps!

## Step 1: Start the System

```bash
docker-compose up -d
```

## Step 2: Wait for Model Download (First Time Only)

The first time you run this, it will download the LLaMA 2 model (~4GB). This takes 5-10 minutes.

Check progress:
```bash
docker-compose logs -f ollama-init
```

Wait until you see: "Model ready!"

## Step 3: Open Your Interface

Choose your preferred interface:

- **Streamlit** (Recommended): http://localhost:8501
- **Web Interface**: http://localhost:5000

## First Use

1. Click "📖 Load Sample Data" to load example documents
2. Ask a question like: "What is Python?"
3. Get an AI-generated answer based on the documents!

## Stop the System

```bash
docker-compose down
```

## Troubleshooting

**Problem**: Services won't start
- **Solution**: Make sure Docker is running and ports 5000, 8501, 8000, 11434 are free

**Problem**: Slow responses
- **Solution**: Give Docker more RAM (Settings → Resources → Memory → 8GB minimum)

**Problem**: Model download stuck
- **Solution**: Check internet connection, restart: `docker-compose restart ollama ollama-init`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Add your own documents
- Try different questions
- Explore the code to customize

---

That's it! You now have a complete RAG system running locally. 🎉
