#!/bin/bash
# Quick setup script for Ollama models

echo "🚀 Ollama Quick Setup Script"
echo "=============================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for Ollama to be ready..."
sleep 5

# Check if Ollama is ready
until docker exec ollama_service ollama list > /dev/null 2>&1; do
    echo "⏳ Waiting for Ollama service..."
    sleep 2
done

echo "✅ Ollama is ready!"
echo ""
echo "📦 Available Models to Install:"
echo "  1. llama2 (3.8GB) - General purpose, balanced"
echo "  2. mistral (4.1GB) - High quality, efficient"
echo "  3. phi (2.7GB) - Fast, lightweight"
echo "  4. neural-chat (4.1GB) - Optimized for chat"
echo "  5. Skip model installation"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        MODEL="llama2"
        ;;
    2)
        MODEL="mistral"
        ;;
    3)
        MODEL="phi"
        ;;
    4)
        MODEL="neural-chat"
        ;;
    5)
        echo "Skipping model installation"
        MODEL=""
        ;;
    *)
        echo "Invalid choice. Defaulting to llama2"
        MODEL="llama2"
        ;;
esac

if [ ! -z "$MODEL" ]; then
    echo ""
    echo "📥 Pulling $MODEL model (this may take a few minutes)..."
    docker exec -it ollama_service ollama pull $MODEL
    echo ""
    echo "✅ Model installed successfully!"
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📍 Access the application at: http://localhost:5000"
echo ""
echo "💡 Useful Commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - List models: docker exec ollama_service ollama list"
echo "  - Pull more models: docker exec ollama_service ollama pull [model-name]"
echo ""
echo "Happy querying! 🚀"
