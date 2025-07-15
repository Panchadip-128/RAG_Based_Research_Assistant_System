#!/usr/bin/env python3
"""
Create proper Redis search index for retrieval testing
"""

import redis
import json
import numpy as np
from test_light_processor import LightDocumentProcessor

def create_redis_index():
    """Create the Redis search index expected by the retriever"""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Test connection
    try:
        r.ping()
        print("✅ Redis connection successful")
    except:
        print("❌ Redis connection failed")
        return False
    
    # Create search index
    try:
        # Check if index exists
        try:
            r.ft("rag-redis").info()
            print("✅ Index 'rag-redis' already exists")
            return True
        except:
            pass
        
        # Create index with vector field
        from redis.commands.search.field import TextField, VectorField
        from redis.commands.search.indexDefinition import IndexDefinition, IndexType
        
        # Define schema
        schema = (
            TextField("content", weight=1.0),
            TextField("metadata", weight=1.0),
            VectorField("content_vector", 
                       "FLAT", 
                       {"TYPE": "FLOAT32", "DIM": 384, "DISTANCE_METRIC": "COSINE"}
                       )
        )
        
        # Create index
        definition = IndexDefinition(
            prefix=["doc:"],
            index_type=IndexType.HASH
        )
        
        r.ft("rag-redis").create_index(schema, definition=definition)
        print("✅ Created Redis search index 'rag-redis'")
        return True
        
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        return False

def add_sample_documents():
    """Add some sample documents to test retrieval"""
    r = redis.Redis(host='localhost', port=6379, decode_responses=False)
    
    # Process document
    processor = LightDocumentProcessor()
    chunks = processor.process_document("assets/2305.15032v1.pdf")
    
    if not chunks:
        print("❌ No chunks to index")
        return False
    
    print(f"✅ Processing {len(chunks)} chunks")
    
    # Add first 3 chunks with dummy embeddings
    for i, chunk in enumerate(chunks[:3]):
        # Create dummy 384-dimensional embedding
        embedding = np.random.rand(384).astype(np.float32).tobytes()
        
        # Store in Redis
        doc_key = f"doc:{i}"
        r.hset(doc_key, mapping={
            "content": chunk["text"],
            "metadata": json.dumps({
                "page": chunk["page"],
                "source": chunk["source"],
                "file": "2305.15032v1.pdf"
            }),
            "content_vector": embedding
        })
        
        print(f"  📝 Indexed chunk {i+1}: {chunk['text'][:50]}...")
    
    # Verify
    keys = r.keys("doc:*")
    print(f"✅ Redis now has {len(keys)} indexed documents")
    return True

if __name__ == "__main__":
    print("🔧 Setting up Redis for retrieval testing...")
    
    if create_redis_index():
        print("\\n📚 Adding sample documents...")
        if add_sample_documents():
            print("\\n✅ Setup complete! Ready for retrieval testing.")
        else:
            print("\\n❌ Failed to add documents")
    else:
        print("\\n❌ Failed to create index")
