#!/bin/bash

# Configuration
MODEL_PATH="/Volumes/Workspace/Models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

# Check if model exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Model file not found at $MODEL_PATH. Please check the path."
    exit 1
fi

echo "Starting Local LLM Server with model: $MODEL_PATH"
echo "API will be available at http://localhost:8000/v1"
echo "Press Ctrl+C to stop the server."

# Start the server
python3 -m llama_cpp.server --model "$MODEL_PATH" --n_gpu_layers -1 --host 0.0.0.0 --port 8001
