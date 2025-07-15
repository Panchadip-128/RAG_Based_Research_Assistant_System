#!/usr/bin/env python3
"""
Lightweight retriever that uses the same embedding model as dataprep
NO HEAVY DOWNLOADS - reuses existing dataprep container
"""
import os
import redis
import json
from typing import List, Dict, Any
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests

app = FastAPI()

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
INDEX_NAME = os.getenv("INDEX_NAME", "rag-redis")
DATAPREP_URL = os.getenv("DATAPREP_URL", "http://localhost:5006")

redis_client = redis.from_url(REDIS_URL)

class RetrievalRequest(BaseModel):
    text: str
    k: int = 5

class RetrievalResponse(BaseModel):
    retrieved_docs: List[Dict[str, Any]]

def get_embedding_from_dataprep(text: str):
    """Get embedding from dataprep service to ensure same model"""
    try:
        # Use dataprep's embedding endpoint (if available) or create a simple one
        response = requests.post(
            f"{DATAPREP_URL}/embed",
            json={"text": text},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["embedding"]
        else:
            raise Exception(f"Dataprep embedding failed: {response.status_code}")
    except Exception as e:
        print(f"Error getting embedding from dataprep: {e}")
        return None

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@app.post("/v1/retrieval", response_model=RetrievalResponse)
async def retrieve(request: RetrievalRequest):
    try:
        # Get embedding from dataprep service to ensure consistency
        query_embedding = get_embedding_from_dataprep(request.text)
        
        if query_embedding is None:
            raise HTTPException(status_code=500, detail="Failed to get embedding from dataprep")
        
        print(f"Query embedding dimension: {len(query_embedding)}")
        
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
    return {"status": "healthy", "uses_dataprep_embedding": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000)
