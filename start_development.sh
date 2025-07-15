#!/bin/bash

# AI Agents Development Environment Startup Script
# This script handles the WSL/Windows path issues properly

echo "🚀 Starting AI Agents Development Environment..."
echo "=========================================="

# Ensure we're in the right directory
cd /mnt/d/ai-agents

echo "📂 Working directory: $(pwd)"

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"

# Function to check if container is running
check_container() {
    docker ps --format "table {{.Names}}" | grep -q "^$1$"
}

# Start Redis if not running
if ! check_container "redis-stack"; then
    echo "🔄 Starting Redis Stack..."
    docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
    sleep 3
else
    echo "✅ Redis Stack is already running"
fi

# Start Dataprep if not running
if ! check_container "dataprep"; then
    echo "🔄 Starting Dataprep Service..."
    docker run -d --name dataprep -p 6007:6007 ai-agents/dataprep:light
    sleep 3
else
    echo "✅ Dataprep Service is already running"
fi

# Start Retriever if not running
if ! check_container "retriever"; then
    echo "🔄 Starting Retriever Service..."
    docker run -d --name retriever -p 7000:7000 ai-agents/retriever:light
    sleep 3
else
    echo "✅ Retriever Service is already running"
fi

echo ""
echo "🎉 All services started successfully!"
echo "=========================================="
echo "📊 Service Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🔗 Service URLs:"
echo "   Redis UI: http://localhost:8001"
echo "   Dataprep: http://localhost:6007"
echo "   Retriever: http://localhost:7000"

echo ""
echo "✅ Development environment is ready!"
echo "💡 For Git operations, use Windows CMD: cd D:\\ai-agents"
echo "💡 For Docker/Python work, use WSL: cd /mnt/d/ai-agents"
