#!/usr/bin/env python3
"""
Fixed retriever that uses the same embedding model as dataprep
"""
import os
import asyncio
import redis
import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

# Load the exact same model as dataprep
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

app = FastAPI()

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
INDEX_NAME = os.getenv("INDEX_NAME", "rag-redis")

# Connect to Redis
redis_client = redis.from_url(REDIS_URL)

class RetrievalRequest(BaseModel):
    text: str
    k: int = 5
    search_type: str = "similarity"

class RetrievalResponse(BaseModel):
    retrieved_docs: List[Dict[str, Any]]

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_similar_documents(query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
    """Search for similar documents using simple vector comparison"""
    try:
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
        return results[:k]
        
    except Exception as e:
        print(f"Error searching documents: {e}")
        return []

@app.post("/v1/retrieval", response_model=RetrievalResponse)
async def retrieve(request: RetrievalRequest):
    """Retrieve similar documents"""
    try:
        # Generate embedding for the query
        query_embedding = model.encode(request.text)
        print(f"Query embedding shape: {query_embedding.shape}")
        
        # Search for similar documents
        results = search_similar_documents(query_embedding.tolist(), request.k)
        
        # Format results
        retrieved_docs = []
        for result in results:
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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
