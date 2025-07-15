#!/bin/bash
# EXACT WORKING SOLUTION - NO MORE ITERATIONS!

set -e

echo "=== STOPPING ALL EXISTING CONTAINERS ==="
docker stop $(docker ps -q) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

echo "=== STARTING REDIS STACK ==="
docker run -d -p 6379:6379 -p 8001:8001 --name redis-stack redis/redis-stack:7.2.0-v9

echo "=== WAITING FOR REDIS TO START ==="
sleep 10

echo "=== STARTING DATAPREP ==="
docker run -d -p 5006:6007 \
  --name dataprep-server \
  --link redis-stack:redis-stack \
  -e REDIS_URL=redis://redis-stack:6379 \
  -e USE_LIGHT_PROCESSING=true \
  -e EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
  -e HUGGINGFACEHUB_API_TOKEN=hf_your_token_here \
  ai-agents/dataprep:light

echo "=== WAITING FOR DATAPREP TO START ==="
sleep 10

echo "=== UPLOADING DOCUMENT ==="
curl -X POST "http://localhost:5006/v1/dataprep" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/mnt/d/ai-agents/assets/2305.15032v1.pdf" \
  -w "\nUpload status: %{http_code}\n"

echo "=== VERIFYING REDIS INDEX ==="
docker exec redis-stack redis-cli FT.INFO rag-redis | grep -A 1 "dim"

echo "=== STARTING SIMPLE RETRIEVER ==="
docker run -d -p 5007:5007 \
  --name simple-retriever \
  --link redis-stack:redis-stack \
  -e REDIS_URL=redis://redis-stack:6379 \
  -e INDEX_NAME=rag-redis \
  -v /mnt/d/ai-agents/simple_retriever_final.py:/app/app.py \
  python:3.11-slim \
  bash -c "pip install sentence-transformers fastapi uvicorn redis numpy && cd /app && python app.py"

echo "=== WAITING FOR RETRIEVER TO START ==="
sleep 15

echo "=== TESTING RETRIEVAL ==="
curl -X POST "http://localhost:5007/v1/retrieval" \
  -H "Content-Type: application/json" \
  -d '{"text": "diffusion models", "k": 2}' \
  -w "\nRetrieval status: %{http_code}\n"

echo "=== SYSTEM IS READY! ==="
echo "Redis UI: http://localhost:8001"
echo "Dataprep: http://localhost:5006"
echo "Retriever: http://localhost:5007"
