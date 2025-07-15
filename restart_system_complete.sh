#!/bin/bash
# AI Agents System - Complete Restart Script
# Date: July 15, 2025
# Purpose: Restart entire system after shutdown/break

echo "🚀 AI Agents System - Complete Restart"
echo "======================================"

# Change to project directory
cd /mnt/d/ai-agents || { echo "❌ Failed to change directory"; exit 1; }

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker stop redis retriever-redis-server 2>/dev/null || true
docker rm redis retriever-redis-server 2>/dev/null || true

# Create custom network if it doesn't exist
echo "🔧 Setting up Docker network..."
docker network create ai-agents-network 2>/dev/null || echo "  Network already exists"

# Start Redis Stack
echo "🔴 Starting Redis Stack..."
docker run -d --name redis --network ai-agents-network -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to initialize..."
sleep 5

# Verify Redis is running
if ! docker exec redis redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis failed to start"
    exit 1
fi
echo "✅ Redis is ready"

# Recreate Redis search index
echo "🔍 Creating Redis search index..."
docker exec redis redis-cli FT.CREATE rag-redis ON HASH PREFIX 1 doc: SCHEMA content TEXT embedding VECTOR FLAT 6 TYPE FLOAT32 DIM 384 DISTANCE_METRIC COSINE 2>/dev/null || echo "  Index already exists"

# Set environment variables
export REDIS_URL="redis://redis:6379"
export HUGGINGFACEHUB_API_TOKEN="YOUR_HUGGINGFACE_TOKEN"

# Start Retriever Service
echo "🔄 Starting Retriever Service..."
docker run -d --name retriever-redis-server --network ai-agents-network -p 5007:7000 -e REDIS_URL=$REDIS_URL -e HUGGINGFACEHUB_API_TOKEN=$HUGGINGFACEHUB_API_TOKEN ai-agents/retriever:latest

# Wait for Retriever to be ready
echo "⏳ Waiting for Retriever Service..."
sleep 10

# Verify services are running
echo "📊 Checking service status..."
if docker ps | grep -q redis; then
    echo "✅ Redis: Running"
else
    echo "❌ Redis: Not running"
fi

if docker ps | grep -q retriever-redis-server; then
    echo "✅ Retriever: Running"
else
    echo "❌ Retriever: Not running"
fi

# Restore sample data
echo "📚 Restoring sample data..."
if [ -f simple_index.py ]; then
    python3 simple_index.py > /dev/null 2>&1
    echo "✅ Sample data restored"
else
    echo "⚠️  Sample data script not found - you may need to reindex documents"
fi

# Final status check
echo ""
echo "🎯 System Status:"
echo "=================="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ System restart complete!"
echo ""
echo "📋 Quick Tests:"
echo "1. Test Redis: docker exec redis redis-cli ping"
echo "2. Test Retrieval: python3 -c \"import requests; print(requests.post('http://localhost:5007/v1/retrieval', json={'text':'test','embedding':[0.1]*384,'k':3,'search_type':'similarity'}).json())\""
echo "3. Process PDFs: python3 test_light_processor.py"
echo ""
echo "🚀 System is ready for use!"
