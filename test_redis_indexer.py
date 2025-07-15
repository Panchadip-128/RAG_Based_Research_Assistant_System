#!/usr/bin/env python3
"""
Redis indexing script for processed documents
"""
import redis
import json
from sentence_transformers import SentenceTransformer
from test_light_processor import LightDocumentProcessor
import os
from typing import List, Dict, Any

class RedisIndexer:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.processor = LightDocumentProcessor()
        self.index_name = 'research_docs'
        
    def test_redis_connection(self):
        """Test Redis connection"""
        try:
            self.redis_client.ping()
            print("✅ Redis connection successful")
            return True
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            return False
    
    def create_index(self):
        """Create Redis search index"""
        try:
            # Check if index exists
            try:
                self.redis_client.ft(self.index_name).info()
                print(f"✅ Index '{self.index_name}' already exists")
                return True
            except:
                pass
            
            # Create index
            from redis.commands.search.field import TextField, VectorField, NumericField
            from redis.commands.search.indexDefinition import IndexDefinition, IndexType
            
            schema = (
                TextField("$.text", as_name="text"),
                TextField("$.source", as_name="source"),
                NumericField("$.page", as_name="page"),
                VectorField("$.embedding", "FLAT", {
                    "TYPE": "FLOAT32",
                    "DIM": 384,
                    "DISTANCE_METRIC": "COSINE"
                }, as_name="embedding")
            )
            
            definition = IndexDefinition(
                prefix=["doc:"],
                index_type=IndexType.JSON
            )
            
            self.redis_client.ft(self.index_name).create_index(
                schema, definition=definition
            )
            print(f"✅ Created index '{self.index_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error creating index: {e}")
            return False
    
    def index_document(self, file_path: str, max_chunks: int = 10):
        """Index a single document"""
        print(f"📄 Processing: {file_path}")
        
        # Process document
        chunks = self.processor.process_document(file_path)
        if not chunks:
            print(f"❌ No chunks extracted from {file_path}")
            return 0
        
        # Limit chunks for testing
        chunks = chunks[:max_chunks]
        
        # Generate embeddings and store
        indexed_count = 0
        for i, chunk in enumerate(chunks):
            try:
                # Generate embedding
                embedding = self.model.encode(chunk['text']).tolist()
                
                # Create document
                doc = {
                    "text": chunk['text'],
                    "source": f"{file_path}#{chunk['source']}",
                    "page": chunk['page'],
                    "embedding": embedding,
                    "file_path": file_path
                }
                
                # Store in Redis
                doc_key = f"doc:{file_path.replace('/', '_')}_{i}"
                self.redis_client.json().set(doc_key, "$", doc)
                indexed_count += 1
                
                if i % 5 == 0:
                    print(f"  📝 Indexed {i+1}/{len(chunks)} chunks...")
                    
            except Exception as e:
                print(f"❌ Error indexing chunk {i}: {e}")
                continue
        
        print(f"✅ Indexed {indexed_count}/{len(chunks)} chunks from {file_path}")
        return indexed_count
    
    def search_documents(self, query: str, k: int = 5):
        """Search indexed documents"""
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query).tolist()
            
            # Search
            from redis.commands.search.query import Query
            
            # Create vector search query
            base_query = f"*=>[KNN {k} @embedding $vector AS score]"
            query_obj = Query(base_query).return_fields("text", "source", "page", "score").sort_by("score").dialect(2)
            
            # Execute search
            result = self.redis_client.ft(self.index_name).search(
                query_obj, 
                {"vector": query_embedding}
            )
            
            print(f"🔍 Found {len(result.docs)} results for: '{query}'")
            for i, doc in enumerate(result.docs):
                print(f"  {i+1}. [Page {doc.page}] Score: {doc.score:.4f}")
                print(f"     Source: {doc.source}")
                print(f"     Text: {doc.text[:200]}...")
                print()
                
            return result.docs
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

if __name__ == "__main__":
    indexer = RedisIndexer()
    
    # Test connection
    if not indexer.test_redis_connection():
        exit(1)
    
    # Create index
    if not indexer.create_index():
        exit(1)
    
    # Index a sample document
    test_file = "assets/2305.15032v1.pdf"
    if os.path.exists(test_file):
        indexed_count = indexer.index_document(test_file, max_chunks=10)
        
        if indexed_count > 0:
            print(f"\\n🔍 Testing search...")
            indexer.search_documents("BERT distillation", k=3)
    else:
        print(f"❌ Test file not found: {test_file}")
