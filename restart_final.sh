#!/bin/bash
# FINAL SYSTEM RESTART SCRIPT
# Use this script to restart the entire RAG system after shutdown
# Updated: July 15, 2025 - Backend Full Configuration Complete

echo "🚀 FINAL SYSTEM RESTART"
echo "======================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🔍 Checking current system state..."

# Function to check if container exists and is running
check_container() {
    local container_name=$1
    if docker ps -q -f name=$container_name > /dev/null; then
        echo "✅ $container_name is running"
        return 0
    elif docker ps -aq -f name=$container_name > /dev/null; then
        echo "⚠️  $container_name exists but is stopped. Starting..."
        docker start $container_name
        return 0
    else
        echo "❌ $container_name does not exist"
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s $url > /dev/null 2>&1; then
            echo "✅ $service_name is ready"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    echo "❌ $service_name failed to start"
    return 1
}

# Create network if it doesn't exist
echo "🌐 Creating network..."
docker network create ai-agents-network 2>/dev/null || echo "Network already exists"

# Start Redis Stack
echo "🔴 Starting Redis Stack..."
if ! check_container "redis"; then
    docker run -d --name redis \
        --network ai-agents-network \
        -p 6379:6379 \
        -p 8001:8001 \
        redis/redis-stack:latest
fi

# Start MongoDB
echo "🟢 Starting MongoDB..."
if ! check_container "mongodb"; then
    docker run -d --name mongodb \
        --network ai-agents-network \
        -p 27017:27017 \
        mongo:latest
fi

# Start Retriever Service
echo "🔵 Starting Retriever Service..."
if ! check_container "retriever-redis-server"; then
    echo "⚠️  Retriever service needs to be rebuilt. Please run the retriever setup."
    echo "   Expected: retriever-redis-server on port 5007"
else
    echo "✅ Retriever service is available"
fi

# Start Backend Service with FULL CONFIGURATION
echo "🟡 Starting Backend Service (Full Configuration)..."
if ! check_container "backend-rag-full"; then
    echo "🔧 Creating backend container with COMPLETE configuration..."
    docker run -d --name backend-rag-full \
        --network ai-agents-network \
        -p 5008:5008 \
        -e MEGA_SERVICE_PORT=5008 \
        -e EMBEDDING_SERVER_HOST_IP=tei-embedding-service \
        -e EMBEDDING_SERVER_PORT=6006 \
        -e RETRIEVER_SERVICE_HOST_IP=retriever-redis-server \
        -e RETRIEVER_SERVICE_PORT=7000 \
        -e RERANK_SERVER_HOST_IP=tei-reranking-service \
        -e RERANK_SERVER_PORT=8808 \
        -e LLM_SERVER_HOST_IP=vllm-service \
        -e LLM_SERVER_PORT=9009 \
        -e MONGO_HOST=mongodb \
        -e MONGO_PORT=27017 \
        ai-agents/rag/backend:latest
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5  # Give containers time to start
wait_for_service "http://localhost:5008/v1/health_check" "Backend"

# Show system status
echo ""
echo "📊 SYSTEM STATUS:"
echo "================="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(redis|mongodb|retriever|backend)"

# Test services
echo ""
echo "🔍 TESTING SERVICES:"
echo "==================="

# Test Redis
redis_status=$(docker exec redis redis-cli ping 2>/dev/null || echo 'NOT AVAILABLE')
echo "Redis: $redis_status"

# Test Backend
backend_status=$(curl -s http://localhost:5008/v1/health_check | jq -r '.["Service Title"]' 2>/dev/null || echo 'NOT AVAILABLE')
echo "Backend: $backend_status"

# Test Retriever
retriever_status=$(curl -s http://localhost:5007/v1/health_check | jq -r '.["Service Title"]' 2>/dev/null || echo 'NOT AVAILABLE')
echo "Retriever: $retriever_status"

# Test MongoDB
mongodb_status=$(docker exec mongodb mongosh --eval 'db.runCommand("ping").ok' --quiet 2>/dev/null || echo 'NOT AVAILABLE')
echo "MongoDB: $mongodb_status"

echo ""
echo "🎉 SYSTEM RESTART COMPLETE!"
echo "=========================="
echo "📱 Quick Access:"
echo "   Backend API: http://localhost:5008/docs"
echo "   Health Check: http://localhost:5008/v1/health_check"
echo "   Retriever: http://localhost:5007/v1/health_check"
echo ""
echo "🧪 Test System:"
echo "   python3 visual_test_rag.py"
echo "   python3 dashboard.py"
echo ""
echo "📊 System Status:"
echo "   ./system_status.sh"
echo ""
echo "🔧 Backend Configuration:"
echo "   All environment variables set for full RAG pipeline"
echo "   Ready for embedding, reranking, and LLM services"
