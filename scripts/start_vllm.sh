#!/bin/bash

# Start vLLM server with AgentFlow model
# This script starts the vLLM server to serve the agentflow-planner-7b model

set -e

MODEL_NAME="AgentFlow/agentflow-planner-7b"
HOST="0.0.0.0"
PORT="8000"

echo "Starting vLLM server for $MODEL_NAME..."
echo "Host: $HOST"
echo "Port: $PORT"
echo ""

# Check if GPU is available
if command -v nvidia-smi &> /dev/null; then
    echo "✓ GPU detected"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo ""
fi

# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --host "$HOST" \
    --port "$PORT" \
    --dtype auto \
    --max-model-len 8192 \
    --api-key "EMPTY"

# Alternative with more control:
# vllm serve "$MODEL_NAME" \
#     --host "$HOST" \
#     --port "$PORT" \
#     --dtype auto \
#     --max-model-len 8192
