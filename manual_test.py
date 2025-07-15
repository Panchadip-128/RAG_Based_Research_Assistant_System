#!/usr/bin/env python3
"""
Manual test commands to visually verify RAG system
"""

import subprocess
import json
import sys

def run_command(cmd, description):
    """Run a command and show the result"""
    print(f"\n🔍 {description}")
    print(f"💻 Command: {cmd}")
    print("─" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Success!")
            print(result.stdout)
        else:
            print("❌ Failed!")
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout!")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 RAG SYSTEM MANUAL VERIFICATION")
    print("=" * 60)
    
    # Test 1: Check Docker containers
    run_command("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'", 
                "Check running Docker containers")
    
    # Test 2: Test Redis connection
    run_command("docker exec redis redis-cli ping", 
                "Test Redis connection")
    
    # Test 3: Check backend health
    run_command("curl -s http://localhost:5008/v1/health_check | jq .", 
                "Check backend health")
    
    # Test 4: Check retriever health
    run_command("curl -s http://localhost:5007/v1/health_check", 
                "Check retriever health")
    
    # Test 5: Test document retrieval
    run_command('''curl -s -X POST http://localhost:5007/v1/retrieval \
-H "Content-Type: application/json" \
-d '{"text": "BERT transformer", "top_k": 2}' | jq .''', 
                "Test document retrieval")
    
    # Test 6: Check backend API docs
    run_command("curl -s http://localhost:5008/docs | grep -o '<title>.*</title>'", 
                "Check backend API documentation")
    
    # Test 7: List available endpoints
    run_command("curl -s http://localhost:5008/openapi.json | jq '.paths | keys[]'", 
                "List available API endpoints")
    
    # Test 8: Check Redis index
    run_command("docker exec redis redis-cli 'FT.INFO' 'rag-redis' | head -10", 
                "Check Redis search index")
    
    # Test 9: Process a document
    run_command("python3 test_light_processor.py", 
                "Test document processing")
    
    print("\n🎉 Manual verification complete!")
    print("\n📋 Next steps:")
    print("1. Run: python3 dashboard.py - for live monitoring")
    print("2. Visit: http://localhost:5008/docs - for API testing")
    print("3. Run: python3 visual_test_rag.py - for comprehensive testing")

if __name__ == "__main__":
    main()
