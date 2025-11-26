#!/bin/bash

echo "🛑 Stopping Resume Parser Application"
echo ""

echo "📦 Stopping application containers..."
docker-compose down

echo "📦 Stopping Ollama container..."
docker-compose -f docker-compose.ollama.yml down

echo ""
echo "✅ All containers stopped!"
echo ""
echo "To remove volumes (including downloaded models), run:"
echo "   docker-compose -f docker-compose.ollama.yml down -v"
echo ""
