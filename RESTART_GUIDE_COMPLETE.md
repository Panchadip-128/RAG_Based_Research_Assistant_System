# 🚀 AI AGENTS RAG SYSTEM - RESTART GUIDE
**Date**: July 15, 2025  
**Status**: Ready for restart after shutdown/break

---

## 📋 QUICK RESTART (After System Shutdown)

### 1. **Navigate to Project**
```bash
cd /mnt/d/ai-agents
```

### 2. **Start Core Services**
```bash
# Option A: Use automated script
./restart_system_complete.sh

# Option B: Manual startup
docker run -d --name redis --network ai-agents-network -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

### 3. **Start Backend**
```bash
docker run -d --name rag-backend -p 5008:5008 \
  -e MEGA_SERVICE_PORT=5008 \
  -e EMBEDDING_SERVER_HOST_IP=tei-embedding-service \
  -e EMBEDDING_SERVER_PORT=6006 \
  -e RETRIEVER_SERVICE_HOST_IP=retriever \
  -e RETRIEVER_SERVICE_PORT=5010 \
  -e RERANK_SERVER_HOST_IP=tei-reranking-service \
  -e RERANK_SERVER_PORT=8808 \
  -e LLM_SERVER_HOST_IP=vllm-service \
  -e LLM_SERVER_PORT=9009 \
  ai-agents/rag/backend:latest
```

### 4. **Verify Services**
```bash
./system_status.sh
```

---

## 🎯 CURRENT ACHIEVEMENTS

### ✅ **COMPLETED**
- **Redis Stack** - Vector database with search index
- **Retriever Service** - Document retrieval working
- **RAG Backend** - Main orchestrator running
- **Light Processor** - PDF processing with PyMuPDF
- **Document Indexing** - 5 chunks from BERT paper indexed
- **PDF Assets** - 17+ research papers ready

### ⚠️ **PARTIALLY COMPLETE**
- **Backend Integration** - Running but missing dependencies
- **Service Network** - Core services connected, others missing

### ❌ **MISSING**
- **Embedding Service** - TEI embedding service
- **Reranking Service** - TEI reranking service  
- **LLM Service** - VLLM service
- **MongoDB** - Optional document storage

---

## 🔧 YOUR WORKING COMPONENTS

### **Light Processor** (`test_light_processor.py`)
- ✅ Processes PDF documents with PyMuPDF
- ✅ Extracts text without heavy AI models
- ✅ Chunks text into manageable pieces
- ✅ Tested with your research papers

### **Redis Integration**
- ✅ Search index "rag-redis" created
- ✅ 5 documents indexed with embeddings
- ✅ Ready for similarity search

### **Retrieval System**
- ✅ Responds to queries with proper JSON
- ✅ Searches indexed documents
- ✅ Returns structured results

---

## 🚀 NEXT DEVELOPMENT STEPS

### **Option 1: Complete RAG Pipeline**
1. Add missing services (embedding, reranking, LLM)
2. Test end-to-end ChatQnA functionality
3. Process more documents

### **Option 2: Extend Current System**
1. Process all 17+ PDF assets
2. Improve embedding quality
3. Add more document types

### **Option 3: Focus on Light Processor**
1. Enhance text extraction
2. Add support for more file types
3. Improve chunking strategy

---

## 📊 SYSTEM READY FOR

- ✅ **Processing more PDF documents**
- ✅ **Adding missing services**
- ✅ **Testing individual components**
- ✅ **Full system integration**
- ✅ **Scaling to larger document collections**

---

## 🔄 HELPFUL COMMANDS

```bash
# Check system status
./system_status.sh

# Test light processor
python3 test_light_processor.py

# Test retrieval
python3 -c "
import json, subprocess
cmd = ['curl', '-X', 'POST', 'http://localhost:5007/v1/retrieval', 
       '-H', 'Content-Type: application/json',
       '-d', json.dumps({'text': 'BERT', 'k': 3, 'search_type': 'similarity'})]
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
"

# View container logs
docker logs redis
docker logs retriever-redis-server
docker logs rag-backend
```

---

**🎉 SYSTEM SAVED AND READY FOR RESTART!**

Your AI agents RAG system is now properly documented and ready to continue from where you left off after any shutdown or break.
