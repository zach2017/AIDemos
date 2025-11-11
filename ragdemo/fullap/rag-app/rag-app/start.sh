#!/bin/bash

# RAG Application Startup Script
# This script starts the RAG application and provides helpful information

set -e

echo "=================================================="
echo "  RAG Q&A System - Docker Deployment"
echo "=================================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed!"
    echo "Please install docker-compose and try again."
    exit 1
fi

echo "✅ Docker is running"
echo "✅ docker-compose is available"
echo ""

# Start the application
echo "🚀 Starting RAG application..."
echo ""
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
echo ""

# Wait for services to be healthy
sleep 5

echo "=================================================="
echo "  Services Status"
echo "=================================================="
docker-compose ps

echo ""
echo "=================================================="
echo "  Access Your Applications"
echo "=================================================="
echo ""
echo "📱 Streamlit Interface:  http://localhost:8501"
echo "🌐 Web Interface:        http://localhost:5000"
echo "📊 ChromaDB:             http://localhost:8000"
echo "🦙 Ollama:               http://localhost:11434"
echo ""

echo "=================================================="
echo "  First Time Setup"
echo "=================================================="
echo ""
echo "If this is your first time running the application:"
echo "1. Wait 5-10 minutes for the LLaMA 2 model to download"
echo "2. Check download progress: docker-compose logs -f ollama-init"
echo "3. Once ready, load sample data in either interface"
echo ""

echo "=================================================="
echo "  Useful Commands"
echo "=================================================="
echo ""
echo "View logs:           docker-compose logs -f"
echo "Stop application:    docker-compose down"
echo "Restart services:    docker-compose restart"
echo "View this again:     ./start.sh"
echo ""

echo "=================================================="
echo "  Need Help?"
echo "=================================================="
echo ""
echo "📖 Read the README.md for detailed documentation"
echo "🐛 Check logs if something isn't working"
echo "💡 See troubleshooting section in README.md"
echo ""

echo "✅ Application started successfully!"
echo ""
