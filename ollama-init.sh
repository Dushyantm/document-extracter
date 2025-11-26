#!/bin/bash

echo "========================================="
echo "Ollama Initialization Starting..."
echo "========================================="

# Check for GPU availability
echo ""
echo "Checking GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi &> /dev/null; then
        GPU_COUNT=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n1)
        GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n1)
        CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')

        echo "✓ GPU DETECTED!"
        echo "  - GPU Count: ${GPU_COUNT}"
        echo "  - GPU Name: ${GPU_NAME}"
        echo "  - GPU Memory: ${GPU_MEMORY}MB"
        echo "  - CUDA Version: ${CUDA_VERSION}"
        echo "  - Mode: GPU-Accelerated Inference"
        echo ""
    else
        echo "⚠ GPU hardware found but not accessible"
        echo "  - Falling back to CPU mode"
        echo "  - Performance will be slower (15-30s per request)"
        echo ""
        export CUDA_VISIBLE_DEVICES=""
    fi
else
    echo "ℹ No GPU detected (nvidia-smi not found)"
    echo "  - Running in CPU-only mode"
    echo "  - Performance: 15-30s per request"
    echo "  - For GPU acceleration, ensure NVIDIA Container Toolkit is installed"
    echo ""
    export CUDA_VISIBLE_DEVICES=""
fi

# Start Ollama in the background
echo "Starting Ollama server..."
/bin/ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama server to initialize..."
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

echo ""
echo "========================================="
echo "✓ Ollama initialization complete!"
echo "========================================="
echo "Server is running with model: ${OLLAMA_MODEL:-gemma3:4b}"

# Show final status
if [ -z "$CUDA_VISIBLE_DEVICES" ] && command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    echo "Status: GPU-Accelerated (CUDA enabled)"
    echo "Expected performance: 2-5 seconds per request"
else
    echo "Status: CPU-only mode"
    echo "Expected performance: 15-30 seconds per request"
fi
echo "========================================="
echo ""

# Keep the container running by waiting for the Ollama process
wait $OLLAMA_PID
