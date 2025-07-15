#!/usr/bin/env python3
"""
FINAL WORKING RETRIEVER - EXACT SAME MODEL AS DATAPREP
"""
import os
import redis
import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import uvicorn

# EXACT SAME MODEL AS DATAPREP
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
print(f"Loading embedding model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)

app = FastAPI()

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
INDEX_NAME = os.getenv("INDEX_NAME", "rag-redis")

print(f"Connecting to Redis: {REDIS_URL}")
redis_client = redis.from_url(REDIS_URL)

class RetrievalRequest(BaseModel):
    text: str
    k: int = 5

class RetrievalResponse(BaseModel):
    retrieved_docs: List[Dict[str, Any]]

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@app.post("/v1/retrieval", response_model=RetrievalResponse)
async def retrieve(request: RetrievalRequest):
    try:
        # Generate embedding for the query - EXACT SAME AS DATAPREP
        query_embedding = model.encode(request.text)
        print(f"Query embedding shape: {query_embedding.shape}")
        
        # Get all document keys
        keys = redis_client.keys(f"doc:{INDEX_NAME}:*")
        print(f"Found {len(keys)} documents in Redis")
        
        results = []
        query_vector = np.array(query_embedding)
        
        for key in keys:
            doc_data = redis_client.hgetall(key)
            if not doc_data:
                continue
                
            # Get the stored vector
            vector_bytes = doc_data.get(b'content_vector')
            if not vector_bytes:
                continue
                
            # Convert bytes to numpy array
            stored_vector = np.frombuffer(vector_bytes, dtype=np.float32)
            
            # Skip if dimensions don't match
            if len(stored_vector) != len(query_vector):
                print(f"Dimension mismatch: stored={len(stored_vector)}, query={len(query_vector)}")
                continue
            
            # Calculate similarity
            similarity = cosine_similarity(query_vector, stored_vector)
            
            # Get text content
            content = doc_data.get(b'content', b'').decode('utf-8')
            
            results.append({
                'text': content,
                'similarity': float(similarity),
                'metadata': {
                    'id': key.decode('utf-8'),
                    'source': doc_data.get(b'source', b'').decode('utf-8')
                }
            })
        
        # Sort by similarity and return top k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Format results
        retrieved_docs = []
        for result in results[:request.k]:
            retrieved_docs.append({
                'text': result['text'],
                'metadata': result['metadata']
            })
        
        return RetrievalResponse(retrieved_docs=retrieved_docs)
        
    except Exception as e:
        print(f"Error in retrieval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "model": MODEL_NAME}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5007)
