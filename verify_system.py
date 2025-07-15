#!/usr/bin/env python3
"""
Quick System Verification Script
Run this after restart to verify everything is working
"""

import subprocess
import requests
import json
import time
import redis

def check_docker_containers():
    """Check if required Docker containers are running"""
    try:
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                              capture_output=True, text=True)
        containers = result.stdout.strip().split('\n')
        
        redis_running = 'redis' in containers
        retriever_running = 'retriever-redis-server' in containers
        
        print("🐳 Docker Containers:")
        print(f"  Redis: {'✅ Running' if redis_running else '❌ Not running'}")
        print(f"  Retriever: {'✅ Running' if retriever_running else '❌ Not running'}")
        
        return redis_running and retriever_running
    except Exception as e:
        print(f"❌ Error checking containers: {e}")
        return False

def check_redis_connection():
    """Check Redis connection and data"""
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        
        # Check data count
        keys = r.keys('doc:*')
        
        # Check index
        try:
            index_info = r.ft('rag-redis').info()
            index_exists = True
        except:
            index_exists = False
        
        print("🔴 Redis Status:")
        print(f"  Connection: ✅ Connected")
        print(f"  Documents: {len(keys)} indexed")
        print(f"  Search Index: {'✅ Exists' if index_exists else '❌ Missing'}")
        
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def check_retriever_api():
    """Check Retriever API endpoint"""
    try:
        # Test with simple embedding
        test_data = {
            "text": "test query",
            "embedding": [0.1] * 384,  # 384-dimensional test embedding
            "k": 3,
            "search_type": "similarity"
        }
        
        response = requests.post(
            'http://localhost:5007/v1/retrieval',
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("🔄 Retriever API:")
            print(f"  Endpoint: ✅ Responding")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {len(result.get('retrieved_docs', []))} docs found")
            return True
        else:
            print(f"❌ Retriever API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Retriever API failed: {e}")
        return False

def test_document_processing():
    """Test document processing"""
    try:
        from test_light_processor import LightDocumentProcessor
        
        processor = LightDocumentProcessor()
        test_file = "assets/2305.15032v1.pdf"
        
        if Path(test_file).exists():
            chunks = processor.process_document(test_file)
            print("📄 Document Processing:")
            print(f"  Test file: ✅ Found")
            print(f"  Chunks extracted: {len(chunks)}")
            return len(chunks) > 0
        else:
            print("📄 Document Processing:")
            print(f"  Test file: ❌ Not found")
            return False
            
    except Exception as e:
        print(f"❌ Document processing failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 AI Agents System Verification")
    print("=" * 40)
    
    # Wait a moment for services to stabilize
    time.sleep(2)
    
    # Run all checks
    containers_ok = check_docker_containers()
    redis_ok = check_redis_connection()
    api_ok = check_retriever_api()
    
    print("\n📊 System Summary:")
    print("=" * 20)
    
    if containers_ok and redis_ok and api_ok:
        print("✅ ALL SYSTEMS OPERATIONAL")
        print("\n🚀 Ready for:")
        print("  - Document processing")
        print("  - Vector search")
        print("  - API queries")
        print("\n📋 Next steps:")
        print("  1. Process more PDFs: python3 test_light_processor.py")
        print("  2. Test retrieval: python3 generate_test_embedding.py")
        print("  3. Continue development")
    else:
        print("❌ SYSTEM ISSUES DETECTED")
        print("\n🔧 Troubleshooting:")
        if not containers_ok:
            print("  - Run: ./restart_system_complete.sh")
        if not redis_ok:
            print("  - Check Redis: docker logs redis")
        if not api_ok:
            print("  - Check Retriever: docker logs retriever-redis-server")

if __name__ == "__main__":
    from pathlib import Path
    main()
