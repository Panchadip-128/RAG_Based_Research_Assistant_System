# AI Agents System - Quick Start Guide
**After Shutdown/Break - Follow These Steps**

## 🚀 **Quick Restart (2 minutes):**

### **Step 1: Navigate to Project**
```bash
cd /mnt/d/ai-agents  # For WSL
# OR
cd D:\ai-agents      # For Windows CMD
```

### **Step 2: Start System**
```bash
./restart_system_complete.sh
```

### **Step 3: Verify Everything Works**
```bash
python3 verify_system.py
```

## 📋 **Expected Output:**
```
🔍 AI Agents System Verification
========================================
🐳 Docker Containers:
  Redis: ✅ Running
  Retriever: ✅ Running
🔴 Redis Status:
  Connection: ✅ Connected
  Documents: 5 indexed
  Search Index: ✅ Exists
🔄 Retriever API:
  Endpoint: ✅ Responding
  Status: 200
  Response: 0 docs found
📊 System Summary:
====================
✅ ALL SYSTEMS OPERATIONAL
```

## 🔧 **Manual Commands (if needed):**

### **Start Services:**
```bash
# Redis
docker run -d --name redis --network ai-agents-network -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

# Retriever
export REDIS_URL="redis://redis:6379"
docker run -d --name retriever-redis-server --network ai-agents-network -p 5007:7000 -e REDIS_URL=$REDIS_URL -e HUGGINGFACEHUB_API_TOKEN=$HUGGINGFACEHUB_API_TOKEN ai-agents/retriever:latest
```

### **Test Commands:**
```bash
# Test PDF processing
python3 test_light_processor.py

# Test retrieval
python3 generate_test_embedding.py

# Test API directly
curl -X POST http://localhost:5007/v1/retrieval -H 'Content-Type: application/json' -d '{"text":"test","embedding":[0.1],"k":3,"search_type":"similarity"}'
```

## 📁 **Key Files Saved:**
- `CURRENT_STATE_FINAL.md` - Complete system status
- `restart_system_complete.sh` - Full restart script
- `verify_system.py` - System verification
- `test_light_processor.py` - Document processing
- `generate_test_embedding.py` - Embedding generation
- `assets/` - Your PDF collection (17+ research papers)

## 🎯 **What's Preserved:**
- ✅ All Docker images built
- ✅ PDF processing pipeline
- ✅ Redis search index configuration
- ✅ Network setup
- ✅ Environment variables
- ✅ Test scripts

## 🚨 **If Issues Occur:**
1. Check Docker: `docker ps`
2. Check logs: `docker logs redis` / `docker logs retriever-redis-server`
3. Recreate network: `docker network create ai-agents-network`
4. Rebuild if needed: `docker build -t ai-agents/retriever:latest -f comps/retriever/Dockerfile .`

## 🎉 **System Ready For:**
- Processing more PDFs from your assets collection
- Implementing real embedding generation
- Building web interfaces
- Scaling to production

**Everything is saved and ready to continue! 🚀**
