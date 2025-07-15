#!/usr/bin/env python3

import os
import json
import redis
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
INDEX_NAME = os.getenv("INDEX_NAME", "research_docs")

class RetrievalRequest(BaseModel):
    text: str
    search_type: str = "similarity"
    k: int = 5

class RetrievalResponse(BaseModel):
    retrieved_docs: List[Dict[str, Any]]
    query: str

class SimpleRetriever:
    def __init__(self):
        self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        self.embedder = SentenceTransformer(EMBED_MODEL)
        logger.info(f"Initialized with model: {EMBED_MODEL}")
        logger.info(f"Redis URL: {REDIS_URL}")
        logger.info(f"Index name: {INDEX_NAME}")
    
    def get_query_embedding(self, text: str) -> List[float]:
        """Generate embedding for query text"""
        embedding = self.embedder.encode(text)
        return embedding.tolist()
    
    def search_similar_docs(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using Redis vector search"""
        try:
            # Get query embedding
            query_embedding = self.get_query_embedding(query)
            
            # Prepare the query vector as bytes
            query_vector = np.array(query_embedding, dtype=np.float32).tobytes()
            
            # Redis search query with vector similarity
            search_query = f"*=>[KNN {k} @vector $query_vector AS similarity_score]"
            
            # Execute the search
            results = self.redis_client.execute_command(
                "FT.SEARCH", INDEX_NAME, search_query, 
                "PARAMS", "2", "query_vector", query_vector,
                "DIALECT", "2",
                "RETURN", "6", "content", "source", "page", "similarity_score"
            )
            
            # Parse results
            docs = []
            if len(results) > 1:
                num_results = results[0]
                logger.info(f"Found {num_results} results")
                
                # Results come in pairs: [doc_id, [field1, value1, field2, value2, ...]]
                for i in range(1, len(results), 2):
                    doc_id = results[i]
                    doc_data = results[i + 1]
                    
                    # Parse document data
                    doc = {"id": doc_id}
                    for j in range(0, len(doc_data), 2):
                        field = doc_data[j]
                        value = doc_data[j + 1]
                        doc[field] = value
                    
                    docs.append(doc)
            
            return docs
            
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Initialize the retriever
retriever = SimpleRetriever()

# FastAPI app
app = FastAPI(title="Simple Document Retriever")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": EMBED_MODEL}

@app.post("/v1/retrieval", response_model=RetrievalResponse)
async def retrieve_documents(request: RetrievalRequest):
    """Retrieve similar documents for a query"""
    try:
        docs = retriever.search_similar_docs(request.text, request.k)
        
        return RetrievalResponse(
            retrieved_docs=docs,
            query=request.text
        )
    except Exception as e:
        logger.error(f"Retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting Simple Document Retriever")
    uvicorn.run(app, host="0.0.0.0", port=7000)
