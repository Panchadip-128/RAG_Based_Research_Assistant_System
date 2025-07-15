#!/bin/bash

# Complete AI Agents Setup Script - Lightweight Version
# This script sets up everything step by step to avoid configuration conflicts

set -e  # Exit on any error

echo "🚀 Starting AI Agents Lightweight Setup..."

# Configuration
export EMBED_MODEL="sentence-transformers/all-MiniLM-L6-v2"
export USE_LIGHT_PROCESSING="true"
export HUGGINGFACEHUB_API_TOKEN="YOUR_HF_TOKEN_HERE"
export REDIS_URL="redis://redis-stack:6379"

echo "📋 Configuration:"
echo "  - Embedding Model: $EMBED_MODEL"
echo "  - Light Processing: $USE_LIGHT_PROCESSING"
echo "  - HuggingFace Token: ${HUGGINGFACEHUB_API_TOKEN:0:10}..."
echo ""

# Step 1: Start Redis
echo "🔴 Step 1: Starting Redis Stack..."
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:7.2.0-v9
sleep 5
echo "✅ Redis Stack started"

# Step 2: Start Dataprep
echo "🔴 Step 2: Starting Dataprep (Light Processing)..."
docker run -d --name dataprep-server -p 5006:6007 \
  --link redis-stack:redis-stack \
  -e http_proxy=$http_proxy \
  -e https_proxy=$https_proxy \
  -e HUGGINGFACEHUB_API_TOKEN=$HUGGINGFACEHUB_API_TOKEN \
  -e REDIS_URL=$REDIS_URL \
  -e EMBED_MODEL=$EMBED_MODEL \
  -e USE_LIGHT_PROCESSING=$USE_LIGHT_PROCESSING \
  -v ~/.cache/huggingface/hub:/.cache/huggingface/hub \
  -v /mnt/d/ai-agents/assets:/tmp/assets \
  ai-agents/dataprep:light

echo "⏳ Waiting for dataprep to start..."
sleep 15

# Step 3: Upload a test document
echo "🔴 Step 3: Uploading test document..."
curl -X POST "http://localhost:5006/v1/dataprep" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/mnt/d/ai-agents/assets/2305.15032v1.pdf" \
  -w "\nUpload status: %{http_code}\n"

echo "⏳ Waiting for document processing..."
sleep 10

# Step 4: Check Redis index
echo "🔴 Step 4: Checking Redis index..."
DIMENSIONS=$(docker exec redis-stack redis-cli FT.INFO rag-redis | grep -A 1 "dim" | tail -1)
NUM_DOCS=$(docker exec redis-stack redis-cli FT.INFO rag-redis | grep -A 1 "num_docs" | tail -1)
echo "  - Vector dimensions: $DIMENSIONS"
echo "  - Number of documents: $NUM_DOCS"

# Step 5: Start Retriever
echo "🔴 Step 5: Starting Retriever..."
docker run -d --name retriever-redis-server -p 5007:7000 \
  --link redis-stack:redis-stack \
  -e http_proxy=$http_proxy \
  -e https_proxy=$https_proxy \
  -e REDIS_URL=$REDIS_URL \
  -e EMBED_MODEL=$EMBED_MODEL \
  -e HUGGINGFACEHUB_API_TOKEN=$HUGGINGFACEHUB_API_TOKEN \
  ai-agents/retriever:latest

echo "⏳ Waiting for retriever to start..."
sleep 20

# Step 6: Test retrieval
echo "🔴 Step 6: Testing retrieval..."
RESPONSE=$(curl -s -X POST "http://localhost:5007/v1/retrieval" \
  -H "Content-Type: application/json" \
  -d '{"text": "machine learning", "k": 2}' \
  -w "\nHTTP_STATUS:%{http_code}")

echo "Response:"
echo "$RESPONSE"

# Step 7: Show final status
echo ""
echo "🎉 Setup Complete!"
echo "📊 Service Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(redis|dataprep|retriever)"

echo ""
echo "🌐 Access Points:"
echo "  - Redis UI: http://localhost:8001"
echo "  - Dataprep API: http://localhost:5006"
echo "  - Retriever API: http://localhost:5007"
echo ""
echo "🧪 Test Commands:"
echo "  # Upload document:"
echo "  curl -X POST \"http://localhost:5006/v1/dataprep\" -H \"Content-Type: multipart/form-data\" -F \"files=@/path/to/file.pdf\""
echo ""
echo "  # Query documents:"
echo "  curl -X POST \"http://localhost:5007/v1/retrieval\" -H \"Content-Type: application/json\" -d '{\"text\": \"your query\", \"k\": 3}'"
