# AI Agents System - Restart Guide

## Quick Start After System Restart

### 1. Navigate to Project Directory

**For WSL (Recommended for Docker/Python work):**
```bash
cd /mnt/d/ai-agents
```

**For Windows CMD (For Git operations):**
```cmd
cd D:\ai-agents
```

### 2. Start the System (Use WSL for Docker)

**In WSL Terminal:**
```bash
# Option A: Use the automated restart script
./restart_system.sh

# Option B: Manual startup (if script fails)
# Start Redis
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

# Start Dataprep Service
docker run -d --name dataprep -p 6007:6007 ai-agents/dataprep:light

# Start Retriever Service
docker run -d --name retriever -p 7000:7000 ai-agents/retriever:light
```

### 3. Verify System Status (Use WSL)

**In WSL Terminal:**
```bash
# Check if all containers are running
docker ps

# Test the services
curl http://localhost:6007/v1/health  # Dataprep
curl http://localhost:7000/v1/health  # Retriever
curl http://localhost:8001            # Redis UI
```

### 4. Process Documents (Use WSL)

**In WSL Terminal:**
```bash
# Process a single PDF
curl -X POST http://localhost:6007/v1/dataprep \
  -H "Content-Type: application/json" \
  -d '{"files": ["assets/your-document.pdf"]}'

# Check processing status
curl http://localhost:6007/v1/dataprep/status
```

### 5. Test Retrieval (Use WSL)

**In WSL Terminal:**
```bash
# Test document retrieval
curl -X POST http://localhost:7000/v1/retrieval \
  -H "Content-Type: application/json" \
  -d '{"text": "your search query", "top_k": 5}'
```

### 6. Git Operations (Use Windows CMD)

**In Windows CMD:**
```cmd
cd D:\ai-agents
git status
git add .
git commit -m "Your message"
git push
```

## Important Notes

### File Locations
- **Project Root**: `D:\ai-agents`
- **PDFs**: `assets/` and `design-patterns/student-companion/ui/public/`
- **Code**: All Python files in `comps/`
- **Docker**: Container configurations in `install/docker/`

### Configuration
- **Redis**: Port 6379 (API), 8001 (UI)
- **Dataprep**: Port 6007
- **Retriever**: Port 7000
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)

### GitHub Repository
- **URL**: https://github.com/Panchadip-128/opea.git
- **Status**: All code saved, PDFs excluded
- **Tokens**: Cleaned and replaced with placeholders

### Troubleshooting
If services don't start:
1. Check Docker is running: `docker --version`
2. Remove old containers: `docker rm -f redis-stack dataprep retriever`
3. Check logs: `docker logs [container-name]`
4. Rebuild if needed: `docker build -t ai-agents/dataprep:light comps/dataprep/`

## Next Steps After Restart
1. ✅ System containers running
2. ✅ Services responding to health checks
3. ✅ Test document processing
4. ✅ Verify retrieval functionality
5. ✅ Continue development work

Last Updated: $(date)
