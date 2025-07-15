@echo off
echo ===============================
echo RAG System Test
echo ===============================
echo.

echo Step 1: Service Health Checks...
echo Testing Backend Health...
curl -s http://localhost:5008/v1/health_check
echo.

echo Testing Retriever Health...
curl -s http://localhost:5007/v1/health_check
echo.

echo Step 2: Container Status...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo Step 3: Testing Document Processing...
python3 test_light_processor.py
echo.

echo Step 4: Testing Visual RAG System...
python3 visual_test_rag.py
echo.

echo Step 5: Available Services...
echo - Backend API: http://localhost:5008/docs
echo - Health Check: http://localhost:5008/v1/health_check
echo - Retriever: http://localhost:5007
echo - Redis: localhost:6379
echo - MongoDB: localhost:27017
echo.

echo ===============================
echo Test Complete!
echo ===============================
