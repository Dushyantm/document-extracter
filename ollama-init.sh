#!/bin/bash

# Start Ollama in the background
/bin/ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama server to start..."
sleep 5

# Try to connect to Ollama using ollama list command
MAX_RETRIES=30
RETRY_COUNT=0
until ollama list > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "ERROR: Ollama server failed to start after ${MAX_RETRIES} seconds"
        exit 1
    fi
    echo "Waiting for Ollama server... (${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 1
done
echo "Ollama server is ready!"

# Pull the model if it doesn't exist
echo "Checking for model: ${OLLAMA_MODEL:-gemma3:4b}..."
if ! ollama list | grep -q "${OLLAMA_MODEL:-gemma3:4b}"; then
    echo "Model not found. Downloading ${OLLAMA_MODEL:-gemma3:4b}..."
    echo "This may take several minutes depending on your internet connection..."
    ollama pull "${OLLAMA_MODEL:-gemma3:4b}"
    if [ $? -eq 0 ]; then
        echo "Model downloaded successfully!"
    else
        echo "ERROR: Failed to download model"
        exit 1
    fi
else
    echo "Model ${OLLAMA_MODEL:-gemma3:4b} already exists."
fi

echo "Ollama initialization complete!"
echo "Server is running with model: ${OLLAMA_MODEL:-gemma3:4b}"

# Keep the container running by waiting for the Ollama process
wait $OLLAMA_PID
