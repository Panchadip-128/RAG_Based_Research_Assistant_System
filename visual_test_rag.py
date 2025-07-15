#!/usr/bin/env python3
"""
Visual test to check and confirm RAG system is working
"""

import requests
import json
import time
from pathlib import Path
import redis
import sys

class RAGSystemTester:
    def __init__(self):
        self.redis_host = "localhost"
        self.redis_port = 6379
        self.retriever_url = "http://localhost:5007"
        self.backend_url = "http://localhost:5008"
        self.test_results = []
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
    
    def print_success(self, message):
        print(f"✅ {message}")
        self.test_results.append(("PASS", message))
    
    def print_error(self, message):
        print(f"❌ {message}")
        self.test_results.append(("FAIL", message))
    
    def print_info(self, message):
        print(f"ℹ️  {message}")
    
    def test_redis_connection(self):
        """Test Redis connection and check indexed documents"""
        self.print_header("TESTING REDIS CONNECTION")
        
        try:
            r = redis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True)
            
            # Test connection
            r.ping()
            self.print_success("Redis connection successful")
            
            # Check if index exists
            try:
                info = r.execute_command("FT.INFO", "rag-redis")
                self.print_success("Redis index 'rag-redis' exists")
                
                # Get document count
                search_result = r.execute_command("FT.SEARCH", "rag-redis", "*", "LIMIT", "0", "0")
                doc_count = search_result[0]
                self.print_success(f"Found {doc_count} documents in Redis index")
                
                # Show sample documents
                if doc_count > 0:
                    sample_docs = r.execute_command("FT.SEARCH", "rag-redis", "*", "LIMIT", "0", "3")
                    self.print_info(f"Sample documents:")
                    for i in range(1, min(len(sample_docs), 7), 2):
                        doc_id = sample_docs[i]
                        print(f"  📄 Document ID: {doc_id}")
                
            except Exception as e:
                self.print_error(f"Redis index 'rag-redis' not found: {str(e)}")
                
        except Exception as e:
            self.print_error(f"Redis connection failed: {str(e)}")
    
    def test_retriever_service(self):
        """Test retriever service"""
        self.print_header("TESTING RETRIEVER SERVICE")
        
        try:
            # Test health
            response = requests.get(f"{self.retriever_url}/v1/health_check", timeout=5)
            if response.status_code == 200:
                self.print_success("Retriever service is healthy")
            else:
                self.print_error(f"Retriever health check failed: {response.status_code}")
                
            # Test retrieval
            test_query = {"text": "BERT transformer model", "top_k": 3}
            response = requests.post(f"{self.retriever_url}/v1/retrieval", 
                                   json=test_query, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                self.print_success(f"Retrieval successful - got {len(results)} results")
                
                # Show retrieved documents
                for i, result in enumerate(results[:2]):
                    print(f"  📄 Result {i+1}:")
                    print(f"     Score: {result.get('score', 'N/A')}")
                    print(f"     Text: {result.get('text', 'N/A')[:150]}...")
                    print()
            else:
                self.print_error(f"Retrieval failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.print_error(f"Retriever service test failed: {str(e)}")
    
    def test_backend_service(self):
        """Test backend service"""
        self.print_header("TESTING BACKEND SERVICE")
        
        try:
            # Test health
            response = requests.get(f"{self.backend_url}/v1/health_check", timeout=5)
            if response.status_code == 200:
                health_info = response.json()
                self.print_success("Backend service is healthy")
                self.print_info(f"Service: {health_info.get('Service Title', 'N/A')}")
            else:
                self.print_error(f"Backend health check failed: {response.status_code}")
            
            # Test API documentation
            response = requests.get(f"{self.backend_url}/docs", timeout=5)
            if response.status_code == 200:
                self.print_success("API documentation is accessible")
            else:
                self.print_error(f"API documentation failed: {response.status_code}")
                
            # Test endpoints listing
            response = requests.get(f"{self.backend_url}/openapi.json", timeout=5)
            if response.status_code == 200:
                api_spec = response.json()
                endpoints = list(api_spec.get('paths', {}).keys())
                self.print_success(f"Found {len(endpoints)} API endpoints")
                self.print_info("Available endpoints:")
                for endpoint in endpoints[:10]:  # Show first 10
                    print(f"  🔗 {endpoint}")
                    
        except Exception as e:
            self.print_error(f"Backend service test failed: {str(e)}")
    
    def test_document_processing(self):
        """Test document processing with the light processor"""
        self.print_header("TESTING DOCUMENT PROCESSING")
        
        try:
            # Import and test the light processor
            sys.path.append('.')
            from test_light_processor import LightDocumentProcessor
            
            processor = LightDocumentProcessor()
            
            # Test with available PDF
            test_files = [
                "assets/2305.15032v1.pdf",
                "assets/grade-7-history.pdf",
                "assets/2401.13138v6.pdf"
            ]
            
            processed_any = False
            for test_file in test_files:
                if Path(test_file).exists():
                    self.print_info(f"Processing {test_file}...")
                    chunks = processor.process_document(test_file)
                    
                    if chunks:
                        self.print_success(f"Processed {len(chunks)} chunks from {test_file}")
                        
                        # Show sample chunks
                        print(f"  📄 Sample chunk from page {chunks[0]['page']}:")
                        print(f"     {chunks[0]['text'][:200]}...")
                        processed_any = True
                        break
                    else:
                        self.print_error(f"No chunks extracted from {test_file}")
                        
            if not processed_any:
                self.print_error("No PDF files found to process")
                
        except Exception as e:
            self.print_error(f"Document processing test failed: {str(e)}")
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        self.print_header("TESTING END-TO-END WORKFLOW")
        
        try:
            # Step 1: Query retriever directly
            self.print_info("Step 1: Querying retriever service...")
            query = {"text": "What is BERT?", "top_k": 2}
            response = requests.post(f"{self.retriever_url}/v1/retrieval", 
                                   json=query, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                self.print_success(f"Retriever returned {len(results)} results")
                
                if results:
                    self.print_info("Top retrieval result:")
                    print(f"  Score: {results[0].get('score', 'N/A')}")
                    print(f"  Text: {results[0].get('text', 'N/A')[:300]}...")
                else:
                    self.print_info("No results found (empty index or no matches)")
                    
            else:
                self.print_error(f"Retriever query failed: {response.status_code}")
                
            # Step 2: Test backend metrics
            self.print_info("Step 2: Checking backend metrics...")
            response = requests.get(f"{self.backend_url}/metrics", timeout=5)
            
            if response.status_code == 200:
                metrics = response.text
                request_count = metrics.count('http_requests_total')
                self.print_success(f"Backend metrics accessible (found {request_count} request metrics)")
            else:
                self.print_error(f"Backend metrics failed: {response.status_code}")
                
        except Exception as e:
            self.print_error(f"End-to-end workflow test failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests and show summary"""
        print(f"\n🚀 STARTING RAG SYSTEM VISUAL TEST")
        print(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        self.test_redis_connection()
        self.test_retriever_service()
        self.test_backend_service()
        self.test_document_processing()
        self.test_end_to_end_workflow()
        
        # Summary
        self.print_header("TEST SUMMARY")
        
        passed = sum(1 for status, _ in self.test_results if status == "PASS")
        failed = sum(1 for status, _ in self.test_results if status == "FAIL")
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {len(self.test_results)}")
        
        if failed == 0:
            print(f"\n🎉 ALL TESTS PASSED! Your RAG system is working correctly!")
        else:
            print(f"\n⚠️  Some tests failed. Check the details above.")
            
        # Show failed tests
        if failed > 0:
            print(f"\n❌ Failed tests:")
            for status, message in self.test_results:
                if status == "FAIL":
                    print(f"  • {message}")

if __name__ == "__main__":
    tester = RAGSystemTester()
    tester.run_all_tests()
