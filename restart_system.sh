#!/bin/bash

# Quick Restart Script for AI Agents System
# Run this after PC restart to restore your working system

echo "🚀 Starting AI Agents Document Retrieval System..."
echo "=================================================="

# Navigate to project directory
cd /mnt/d/ai-agents

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker stop redis ai-agents-dataprep-light ai-agents-retriever-lightweight 2>/dev/null || true
docker rm redis ai-agents-dataprep-light ai-agents-retriever-lightweight 2>/dev/null || true

# Start Redis Stack
echo "🔴 Starting Redis Stack..."
docker run -d --name redis -p 6379:6379 redis/redis-stack:7.2.0-v9

# Wait for Redis to start
echo "⏳ Waiting for Redis to initialize..."
sleep 5

# Build and start Dataprep service
echo "📊 Building and starting Dataprep service..."
docker build -f comps/dataprep/Dockerfile -t ai-agents/dataprep:light . || {
    echo "❌ Failed to build dataprep image"
    exit 1
}

docker run -d --name ai-agents-dataprep-light \
  -p 6007:6007 \
  -e REDIS_URL=redis://172.17.0.1:6379 \
  -e EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
  -e USE_LIGHT_PROCESSING=true \
  -e INDEX_NAME=research_docs \
  ai-agents/dataprep:light || {
    echo "❌ Failed to start dataprep service"
    exit 1
}

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Test the system
echo "🧪 Testing system..."
python3 test_retrieval.py

echo ""
echo "🎉 System Status:"
echo "=================="
echo "✅ Redis Stack: http://localhost:8001"
echo "✅ Dataprep API: http://localhost:6007/docs"
echo "✅ Ready to upload documents and test retrieval!"
echo ""
echo "📋 To upload a document:"
echo 'curl -X POST "http://localhost:6007/v1/dataprep" -H "Content-Type: multipart/form-data" -F "files=@assets/grade-7-history.pdf"'
echo ""
echo "🔍 To test retrieval:"
echo 'curl -X POST "http://localhost:7000/v1/retrieval" -H "Content-Type: application/json" -d '\''{"text": "What is the capital of India?", "k": 5}'\'''
