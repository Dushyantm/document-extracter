#!/bin/bash

# Script to manually pull additional Ollama models for the resume parser
# NOTE: The default model (gemma3:4b) downloads automatically on first startup
# This script is only needed for pulling additional models

echo "🚀 Setting up Ollama model for Resume Parser..."
echo "ℹ️  Note: The default model auto-downloads on first startup"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if ollama container is running
if ! docker ps | grep -q "resume-parser-ollama"; then
    echo "❌ Error: Ollama container is not running."
    echo "   Please run 'docker-compose up -d' first."
    exit 1
fi

echo "📥 Pulling Ollama model: gemma3:4b"
echo "   This may take a few minutes depending on your internet connection..."
echo ""

# Pull the model
docker exec -it resume-parser-ollama ollama pull gemma3:4b

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Model pulled successfully!"
    echo ""
    echo "📋 Available models:"
    docker exec -it resume-parser-ollama ollama list
    echo ""
    echo "🎉 Ollama is ready to use!"
    echo ""
    echo "To test the model, run:"
    echo "  docker exec -it resume-parser-ollama ollama run gemma3:4b 'Hello!'"
else
    echo ""
    echo "❌ Failed to pull model. Please check your internet connection and try again."
    exit 1
fi
