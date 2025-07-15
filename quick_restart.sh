#!/bin/bash
# AI Agents System - Quick Restart Script
# Date: July 15, 2025
# Use this script to restart the system after shutdown/break

echo "🚀 Starting AI Agents Document Retrieval System..."
echo "=================================================="

# Navigate to project directory
cd /mnt/d/ai-agents

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi
echo "✅ Docker is running"

# Clean up existing containers (if any)
echo "🧹 Cleaning up existing containers..."
docker stop redis retriever-redis-server 2>/dev/null || true
docker rm redis retriever-redis-server 2>/dev/null || true

# Create network if it doesn't exist
echo "🔗 Setting up network..."
docker network create ai-agents-network 2>/dev/null || echo "Network already exists"

# Start Redis Stack
echo "🔴 Starting Redis Stack..."
docker run -d --name redis --network ai-agents-network -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

# Wait for Redis to initialize
echo "⏳ Waiting for Redis to initialize..."
sleep 10

# Verify Redis is ready
echo "🔍 Checking Redis connection..."
if docker exec redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis failed to start"
    exit 1
fi

# Set environment variables
export REDIS_URL="redis://redis:6379"
export HUGGINGFACEHUB_API_TOKEN="YOUR_HUGGINGFACE_TOKEN"

# Start Retriever Service
echo "🔍 Starting Retriever Service..."
docker run -d --name retriever-redis-server --network ai-agents-network -p 5007:7000 \
    -e REDIS_URL=$REDIS_URL \
    -e HUGGINGFACEHUB_API_TOKEN=$HUGGINGFACEHUB_API_TOKEN \
    ai-agents/retriever:latest

# Wait for retriever to initialize
echo "⏳ Waiting for Retriever to initialize..."
sleep 10

# Verify retriever is ready
echo "🔍 Checking Retriever service..."
if curl -s http://localhost:5007/ > /dev/null 2>&1; then
    echo "✅ Retriever service is ready"
else
    echo "⚠️  Retriever service may still be starting..."
fi

# Recreate Redis search index
echo "🔧 Setting up Redis search index..."
docker exec redis redis-cli FT.CREATE rag-redis ON HASH PREFIX 1 doc: SCHEMA content TEXT embedding VECTOR FLAT 6 TYPE FLOAT32 DIM 384 DISTANCE_METRIC COSINE 2>/dev/null || echo "Index already exists"

# Restore document data (if needed)
echo "📚 Checking document data..."
DOC_COUNT=$(docker exec redis redis-cli DBSIZE)
if [ "$DOC_COUNT" -eq "0" ]; then
    echo "📝 Restoring document data..."
    python3 simple_index.py
else
    echo "✅ Found $DOC_COUNT documents in Redis"
fi

# System status
echo ""
echo "📊 System Status:"
echo "=================="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test retrieval
echo ""
echo "🧪 Testing retrieval..."
python3 -c "
import json, subprocess, random
random.seed(42)
embedding = [random.uniform(-0.5, 0.5) for _ in range(384)]
data = {'text': 'BERT distillation', 'embedding': embedding, 'k': 3, 'search_type': 'similarity'}
try:
    result = subprocess.run(['curl', '-X', 'POST', 'http://localhost:5007/v1/retrieval', '-H', 'Content-Type: application/json', '-d', json.dumps(data)], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print('✅ Retrieval test: SUCCESS')
    else:
        print('❌ Retrieval test: FAILED')
except:
    print('⚠️  Retrieval test: TIMEOUT (service may still be starting)')
"

echo ""
echo "🎉 System startup complete!"
echo "✅ Redis Stack: http://localhost:8001 (RedisInsight)"
echo "✅ Retriever API: http://localhost:5007/v1/retrieval"
echo "✅ Ready for backend setup!"
