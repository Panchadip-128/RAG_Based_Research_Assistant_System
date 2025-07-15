#!/bin/bash

# Configuration script for AI Agents with light processing
# This script helps you run the services with less memory-intensive settings

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 AI Agents - Light Processing Configuration${NC}"
echo "=================================================="

# Default settings for light processing
export EMBED_MODEL="sentence-transformers/all-MiniLM-L6-v2"
export USE_LIGHT_PROCESSING="true"
export HUGGINGFACEHUB_API_TOKEN="YOUR_HF_TOKEN_HERE"
export REDIS_URL="redis://redis-stack:6379"

echo -e "${YELLOW}Configuration:${NC}"
echo "• Embedding Model: $EMBED_MODEL (384 dimensions - lightweight)"
echo "• Light Processing: $USE_LIGHT_PROCESSING (no heavy AI models)"
echo "• Redis URL: $REDIS_URL"
echo ""

# Function to start services
start_services() {
    echo -e "${GREEN}Starting services...${NC}"
    
    # Start Redis Stack
    echo "1. Starting Redis Stack..."
    docker run -d -p 6379:6379 -p 8001:8001 --name redis-stack redis/redis-stack:7.2.0-v9 2>/dev/null || echo "Redis Stack already running"
    
    # Start Dataprep with light processing
    echo "2. Starting Dataprep (Light Processing)..."
    docker run -d -p 5006:6007 \
        --link redis-stack:redis-stack \
        -e http_proxy=$http_proxy \
        -e https_proxy=$https_proxy \
        -e HUGGINGFACEHUB_API_TOKEN=$HUGGINGFACEHUB_API_TOKEN \
        -e REDIS_URL=$REDIS_URL \
        -e EMBED_MODEL=$EMBED_MODEL \
        -e USE_LIGHT_PROCESSING=$USE_LIGHT_PROCESSING \
        -v ~/.cache/huggingface/hub:/.cache/huggingface/hub \
        -v /mnt/d/ai-agents/assets:/tmp/assets \
        --name dataprep-server \
        ai-agents/dataprep:light
    
    # Start Retriever
    echo "3. Starting Retriever..."
    docker run -d -p 5007:7000 \
        --link redis-stack:redis-stack \
        -e http_proxy=$http_proxy \
        -e https_proxy=$https_proxy \
        -e REDIS_URL=$REDIS_URL \
        -e EMBED_MODEL=$EMBED_MODEL \
        -e HUGGINGFACEHUB_API_TOKEN=$HUGGINGFACEHUB_API_TOKEN \
        --name retriever-redis-server \
        ai-agents/retriever:latest
    
    echo -e "${GREEN}✅ All services started!${NC}"
}

# Function to stop services
stop_services() {
    echo -e "${YELLOW}Stopping services...${NC}"
    docker stop dataprep-server retriever-redis-server redis-stack 2>/dev/null || true
    docker rm dataprep-server retriever-redis-server redis-stack 2>/dev/null || true
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Function to test upload
test_upload() {
    echo -e "${GREEN}Testing document upload...${NC}"
    curl -X POST "http://localhost:5006/v1/dataprep" \
        -H "Content-Type: multipart/form-data" \
        -F "files=@/mnt/d/ai-agents/assets/2305.15032v1.pdf"
    echo ""
}

# Function to test retrieval
test_retrieval() {
    echo -e "${GREEN}Testing document retrieval...${NC}"
    curl -X POST "http://localhost:5007/v1/retrieval" \
        -H "Content-Type: application/json" \
        -d '{"text": "machine learning", "k": 3}'
    echo ""
}

# Menu
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    test-upload)
        test_upload
        ;;
    test-retrieval)
        test_retrieval
        ;;
    status)
        echo -e "${GREEN}Service Status:${NC}"
        docker ps | grep -E "(redis-stack|dataprep|retriever)" || echo "No services running"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|test-upload|test-retrieval|status}"
        echo ""
        echo "Commands:"
        echo "  start         - Start all services with light processing"
        echo "  stop          - Stop all services"
        echo "  restart       - Restart all services"
        echo "  test-upload   - Test document upload"
        echo "  test-retrieval - Test document retrieval"
        echo "  status        - Show service status"
        exit 1
        ;;
esac
