#!/usr/bin/env python3
"""
Create proper embeddings for your PDF assets using sentence-transformers
"""

import redis
import numpy as np
from sentence_transformers import SentenceTransformer
from test_light_processor import LightDocumentProcessor

def create_proper_embeddings():
    """Generate real embeddings for your PDF content"""
    
    # Initialize the same model used by the retriever
    print("📥 Loading sentence-transformers model...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    rb = redis.Redis(host='localhost', port=6379, decode_responses=False)
    
    # Get all document keys
    keys = r.keys("doc:*")
    print(f"📚 Processing {len(keys)} documents from your PDF assets...")
    
    for key in keys:
        # Get the actual PDF content
        content = r.hget(key, 'content')
        
        if content:
            # Generate REAL embedding from your PDF content
            print(f"🔄 Generating embedding for: {content[:50]}...")
            embedding = model.encode(content)
            
            # Store the real embedding
            rb.hset(key, 'embedding', embedding.astype(np.float32).tobytes())
            print(f"✅ Updated {key} with real embedding")
        else:
            print(f"⚠️  No content found for {key}")
    
    print(f"\\n✅ Generated real embeddings for {len(keys)} documents from your PDF assets!")
    return len(keys)

def test_retrieval_with_real_embeddings():
    """Test retrieval with real embeddings"""
    print("\\n🔍 Testing retrieval with real embeddings...")
    
    # Load the same model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Test queries related to your PDF content
    test_queries = [
        "BERT distillation",
        "weight initialization", 
        "neural network compression",
        "transformer models"
    ]
    
    for query in test_queries:
        print(f"\\n🔍 Testing query: '{query}'")
        
        # Generate embedding for the query
        query_embedding = model.encode(query).tolist()
        
        # Test with curl (you can copy this)
        print(f"curl -X POST http://localhost:5007/v1/retrieval \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{{\"text\":\"{query}\",\"embedding\":{query_embedding[:3]}...,\"k\":3,\"search_type\":\"similarity\"}}'")

if __name__ == "__main__":
    # Create proper embeddings from your PDF assets
    count = create_proper_embeddings()
    
    if count > 0:
        # Show how to test with real embeddings
        test_retrieval_with_real_embeddings()
    else:
        print("❌ No documents found to process")
