#!/bin/bash

echo "🚀 Starting Resume Parser Application"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Start Ollama container
echo "📦 Starting Ollama container..."
docker-compose -f docker-compose.ollama.yml up -d

echo "⏳ Waiting for Ollama to be ready..."
sleep 5

# Check if Ollama is healthy
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker exec ollama-standalone curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is ready!"
        break
    fi
    echo "   Still waiting... ($((attempt+1))/$max_attempts)"
    sleep 2
    attempt=$((attempt+1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "⚠️  Ollama is taking longer than expected. Check logs:"
    echo "   docker-compose -f docker-compose.ollama.yml logs -f"
    echo ""
    echo "Continuing to start the application..."
fi

echo ""
echo "📦 Starting application containers..."
docker-compose up --build -d

echo ""
echo "✅ Application started!"
echo ""
echo "📍 Access points:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Ollama:    http://localhost:11434"
echo ""
echo "📋 Useful commands:"
echo "   View app logs:    docker-compose logs -f"
echo "   View Ollama logs: docker-compose -f docker-compose.ollama.yml logs -f"
echo "   Stop all:         ./stop.sh"
echo ""
