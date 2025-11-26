#!/bin/bash

# Start Ollama in the background
/bin/ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama server to start..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 1
done
echo "Ollama server is ready!"

# Pull the model if it doesn't exist
echo "Checking for model: ${OLLAMA_MODEL:-gemma3:4b}..."
if ! ollama list | grep -q "${OLLAMA_MODEL:-gemma3:4b}"; then
    echo "Model not found. Downloading ${OLLAMA_MODEL:-gemma3:4b}..."
    ollama pull "${OLLAMA_MODEL:-gemma3:4b}"
    echo "Model downloaded successfully!"
else
    echo "Model ${OLLAMA_MODEL:-gemma3:4b} already exists."
fi

# Keep the container running
wait
