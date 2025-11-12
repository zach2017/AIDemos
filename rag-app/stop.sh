#!/bin/bash

# RAG Application Stop Script

set -e

echo "=================================================="
echo "  Stopping RAG Q&A System"
echo "=================================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    exit 1
fi

echo "🛑 Stopping all services..."
echo ""
docker-compose down

echo ""
echo "✅ All services stopped successfully!"
echo ""
echo "To start again: ./start.sh"
echo "To remove all data: docker-compose down -v"
echo ""
