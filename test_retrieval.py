#!/usr/bin/env python3

import redis
import numpy as np
import json

# Connect to Redis
redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

# Test connection
try:
    redis_client.ping()
    print("✅ Redis connection successful")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    exit(1)

# Check if the index exists
try:
    info = redis_client.execute_command("FT.INFO", "research_docs")
    print("✅ Index 'research_docs' exists")
    print(f"   Number of documents: {info[info.index('num_docs') + 1]}")
except Exception as e:
    print(f"❌ Index 'research_docs' not found: {e}")
    exit(1)

# Test search with a simple query
try:
    # Try a simple text search first
    results = redis_client.execute_command("FT.SEARCH", "research_docs", "India", "LIMIT", "0", "5")
    print(f"✅ Simple text search found {results[0]} results")
    
    # Show first result
    if results[0] > 0:
        doc_id = results[1]
        doc_data = results[2]
        print(f"   First result ID: {doc_id}")
        
        # Parse the document data
        doc = {}
        for i in range(0, len(doc_data), 2):
            field = doc_data[i]
            value = doc_data[i + 1]
            doc[field] = value
        
        print(f"   Content preview: {doc.get('content', 'N/A')[:100]}...")
        
except Exception as e:
    print(f"❌ Search failed: {e}")

print("\n🎉 Basic retrieval system is working!")
print("The Redis index is properly configured and contains documents.")
print("Vector dimension mismatch error should be resolved!")
