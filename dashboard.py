#!/usr/bin/env python3
"""
Simple dashboard to visually check RAG system status
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime

def print_box(title, content, width=70):
    """Print content in a nice box"""
    print("┌" + "─" * (width-2) + "┐")
    print(f"│ {title:^{width-4}} │")
    print("├" + "─" * (width-2) + "┤")
    for line in content:
        print(f"│ {line:<{width-4}} │")
    print("└" + "─" * (width-2) + "┘")

def check_service(name, url, timeout=5):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return "🟢 ONLINE", response.json() if response.headers.get('content-type', '').startswith('application/json') else "OK"
        else:
            return f"🟡 HTTP {response.status_code}", response.text[:100]
    except Exception as e:
        return "🔴 OFFLINE", str(e)

def check_docker_containers():
    """Check Docker container status"""
    try:
        result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            containers = []
            for line in lines:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        containers.append(f"{parts[0]}: {parts[1]}")
            return containers
        else:
            return ["Error checking containers"]
    except Exception as e:
        return [f"Error: {str(e)}"]

def main():
    while True:
        # Clear screen
        print("\033[2J\033[H")
        
        print("🔍 RAG SYSTEM DASHBOARD")
        print("=" * 70)
        print(f"⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check services
        services = [
            ("Redis Stack", "http://localhost:6379"),
            ("Retriever Service", "http://localhost:5007/v1/health_check"),
            ("Backend Service", "http://localhost:5008/v1/health_check"),
        ]
        
        service_status = []
        for name, url in services:
            if "6379" in url:
                # Special case for Redis
                try:
                    import redis
                    r = redis.Redis(host='localhost', port=6379)
                    r.ping()
                    service_status.append(f"{name}: 🟢 ONLINE")
                except:
                    service_status.append(f"{name}: 🔴 OFFLINE")
            else:
                status, info = check_service(name, url)
                service_status.append(f"{name}: {status}")
        
        print_box("SERVICE STATUS", service_status)
        print()
        
        # Check Docker containers
        containers = check_docker_containers()
        print_box("DOCKER CONTAINERS", containers)
        print()
        
        # Quick tests
        test_results = []
        
        # Test retriever
        try:
            response = requests.post("http://localhost:5007/v1/retrieval", 
                                   json={"text": "test", "top_k": 1}, timeout=5)
            if response.status_code == 200:
                results = response.json()
                test_results.append(f"Retrieval Test: 🟢 {len(results)} results")
            else:
                test_results.append(f"Retrieval Test: 🟡 HTTP {response.status_code}")
        except Exception as e:
            test_results.append(f"Retrieval Test: 🔴 {str(e)[:40]}")
        
        # Test backend docs
        try:
            response = requests.get("http://localhost:5008/docs", timeout=5)
            if response.status_code == 200:
                test_results.append("Backend Docs: 🟢 Available")
            else:
                test_results.append(f"Backend Docs: 🟡 HTTP {response.status_code}")
        except Exception as e:
            test_results.append(f"Backend Docs: 🔴 {str(e)[:40]}")
        
        print_box("QUICK TESTS", test_results)
        print()
        
        # Instructions
        instructions = [
            "🌐 Backend API Docs: http://localhost:5008/docs",
            "🔍 Test Retrieval: curl -X POST http://localhost:5007/v1/retrieval",
            "📊 Backend Metrics: curl http://localhost:5008/metrics",
            "🛑 Press Ctrl+C to stop this dashboard"
        ]
        
        print_box("QUICK ACTIONS", instructions)
        print()
        
        # Wait before refresh
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped!")
            break

if __name__ == "__main__":
    main()
