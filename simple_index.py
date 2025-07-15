#!/usr/bin/env python3
"""
Simple document indexing for testing retrieval
"""
import json
import redis
from test_light_processor import LightDocumentProcessor

# Process a document
processor = LightDocumentProcessor()
chunks = processor.process_document("assets/2305.15032v1.pdf")

if chunks:
    print(f"✅ Processed {len(chunks)} chunks")
    
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Store a few chunks for testing
    for i, chunk in enumerate(chunks[:5]):  # Just first 5 chunks
        doc_key = f"doc:{i}"
        doc_data = {
            "text": chunk["text"],
            "page": chunk["page"],
            "source": chunk["source"]
        }
        r.hset(doc_key, mapping=doc_data)
        print(f"  📝 Stored chunk {i+1}: {chunk['text'][:50]}...")
    
    print(f"✅ Indexed {min(5, len(chunks))} chunks in Redis")
    
    # Verify
    keys = r.keys("doc:*")
    print(f"✅ Redis now has {len(keys)} document keys")
    
else:
    print("❌ No chunks to index")
