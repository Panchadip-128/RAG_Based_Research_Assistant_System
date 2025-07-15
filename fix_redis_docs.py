#!/usr/bin/env python3
"""
Fix Redis documents to match the search index schema
"""

import redis
import numpy as np
from test_light_processor import LightDocumentProcessor

def fix_redis_documents():
    """Update existing Redis documents to match search index schema"""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    rb = redis.Redis(host='localhost', port=6379, decode_responses=False)  # For binary data
    
    # Get all document keys
    keys = r.keys("doc:*")
    print(f"Found {len(keys)} documents to fix")
    
    for key in keys:
        # Get existing document
        doc = r.hgetall(key)
        
        if 'text' in doc:
            # Create 384-dimensional embedding (dummy for now)
            embedding = np.random.rand(384).astype(np.float32)
            
            # Update document with correct schema
            rb.hset(key, mapping={
                'content': doc['text'],  # Rename 'text' to 'content'
                'embedding': embedding.tobytes(),  # Add embedding
                'metadata': f"page_{doc.get('page', '1')}"  # Add metadata
            })
            
            print(f"✅ Fixed {key}: {doc['text'][:50]}...")
        else:
            print(f"⚠️  Skipping {key} - no text field")
    
    print(f"\\n✅ Updated {len(keys)} documents")

if __name__ == "__main__":
    fix_redis_documents()
