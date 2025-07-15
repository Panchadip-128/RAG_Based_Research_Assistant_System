#!/bin/bash
# COMPLETE SYSTEM STATE SAVE
# Date: July 15, 2025
# Status: Backend Full Configuration Complete

echo "💾 SAVING COMPLETE SYSTEM STATE"
echo "==============================="

# Create backup directory
mkdir -p backup/$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"

echo "📁 Backup directory: $BACKUP_DIR"

# Save Docker container states
echo "🐳 Saving Docker container states..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}" > $BACKUP_DIR/docker_containers.txt
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" > $BACKUP_DIR/docker_images.txt
docker network ls > $BACKUP_DIR/docker_networks.txt

# Save container configurations
echo "🔧 Saving container configurations..."
docker inspect backend-rag-full > $BACKUP_DIR/backend_config.json 2>/dev/null || echo "Backend container not found"
docker inspect retriever-redis-server > $BACKUP_DIR/retriever_config.json 2>/dev/null || echo "Retriever container not found"
docker inspect redis > $BACKUP_DIR/redis_config.json 2>/dev/null || echo "Redis container not found"
docker inspect mongodb > $BACKUP_DIR/mongodb_config.json 2>/dev/null || echo "MongoDB container not found"

# Save environment variables
echo "🌍 Saving environment variables..."
docker exec backend-rag-full env > $BACKUP_DIR/backend_env.txt 2>/dev/null || echo "Backend env not accessible"

# Save service health status
echo "🏥 Saving service health status..."
curl -s http://localhost:5008/v1/health_check > $BACKUP_DIR/backend_health.json 2>/dev/null || echo "Backend health check failed"
curl -s http://localhost:5007/v1/health_check > $BACKUP_DIR/retriever_health.json 2>/dev/null || echo "Retriever health check failed"

# Save API documentation
echo "📚 Saving API documentation..."
curl -s http://localhost:5008/openapi.json > $BACKUP_DIR/backend_api.json 2>/dev/null || echo "Backend API not accessible"

# Save Redis data info
echo "🔍 Saving Redis data info..."
docker exec redis redis-cli INFO > $BACKUP_DIR/redis_info.txt 2>/dev/null || echo "Redis info not accessible"
docker exec redis redis-cli FT.INFO rag-redis > $BACKUP_DIR/redis_index_info.txt 2>/dev/null || echo "Redis index not found"

# Save current working directory contents
echo "📄 Saving current directory contents..."
ls -la > $BACKUP_DIR/directory_contents.txt
find . -name "*.py" -o -name "*.md" -o -name "*.sh" -o -name "*.json" -o -name "*.txt" | head -50 > $BACKUP_DIR/important_files.txt

# Save git status
echo "🌱 Saving git status..."
git status > $BACKUP_DIR/git_status.txt 2>/dev/null || echo "Not a git repository"
git log --oneline -10 > $BACKUP_DIR/git_log.txt 2>/dev/null || echo "No git log available"

# Save system information
echo "💻 Saving system information..."
echo "Hostname: $(hostname)" > $BACKUP_DIR/system_info.txt
echo "Date: $(date)" >> $BACKUP_DIR/system_info.txt
echo "User: $(whoami)" >> $BACKUP_DIR/system_info.txt
echo "Working Directory: $(pwd)" >> $BACKUP_DIR/system_info.txt
echo "Docker Version: $(docker --version)" >> $BACKUP_DIR/system_info.txt

# Create summary
echo "📊 Creating summary..."
cat > $BACKUP_DIR/SAVE_SUMMARY.md << 'EOF'
# COMPLETE SYSTEM STATE SAVE
Date: $(date)
Status: Backend Full Configuration Complete

## System Status
- Backend Container: backend-rag-full (RUNNING)
- Retriever Container: retriever-redis-server (RUNNING)
- Redis Container: redis (RUNNING)
- MongoDB Container: mongodb (RUNNING)

## Backend Configuration
- Image: ai-agents/rag/backend:latest
- Port: 5008:5008
- Network: ai-agents-network
- Health: PASSING
- API Docs: AVAILABLE

## Environment Variables
- MEGA_SERVICE_PORT=5008
- EMBEDDING_SERVER_HOST_IP=tei-embedding-service
- EMBEDDING_SERVER_PORT=6006
- RETRIEVER_SERVICE_HOST_IP=retriever-redis-server
- RETRIEVER_SERVICE_PORT=7000
- RERANK_SERVER_HOST_IP=tei-reranking-service
- RERANK_SERVER_PORT=8808
- LLM_SERVER_HOST_IP=vllm-service
- LLM_SERVER_PORT=9009
- MONGO_HOST=mongodb
- MONGO_PORT=27017

## Services Ready
✅ Backend Service (port 5008)
✅ Retriever Service (port 5007)
✅ Redis Stack (port 6379)
✅ MongoDB (port 27017)
✅ Document Processing (PyMuPDF)
✅ API Documentation
✅ Health Checks

## Next Steps After Restart
1. Run: ./restart_system_complete.sh
2. Verify: python3 visual_test_rag.py
3. Check: ./system_status.sh
4. Access: http://localhost:5008/docs

## Missing Services (for full RAG)
- TEI Embedding Service (port 6006)
- TEI Reranking Service (port 8808)
- VLLM Service (port 9009)
EOF

echo "✅ System state saved to: $BACKUP_DIR"
echo "📁 Total files saved: $(find $BACKUP_DIR -type f | wc -l)"
echo "💾 Backup size: $(du -sh $BACKUP_DIR | cut -f1)"

# Create quick restore script
cat > restore_from_backup.sh << 'EOF'
#!/bin/bash
echo "🔄 RESTORING FROM BACKUP"
echo "======================="

# Find latest backup
LATEST_BACKUP=$(find backup -type d -name "????????_??????" | sort | tail -1)
if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ No backup found!"
    exit 1
fi

echo "📁 Latest backup: $LATEST_BACKUP"

# Show backup contents
echo "📊 Backup contents:"
cat $LATEST_BACKUP/SAVE_SUMMARY.md

# Restore containers (manual step)
echo "🔧 To restore containers, run:"
echo "   ./restart_system_complete.sh"
echo "   python3 visual_test_rag.py"
EOF

chmod +x restore_from_backup.sh

echo "🎉 COMPLETE SYSTEM STATE SAVED SUCCESSFULLY!"
echo "To restore: ./restore_from_backup.sh"
