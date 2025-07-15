@echo off
echo ===============================
echo RAG System Restart
echo ===============================
echo.

echo Step 1: Checking Docker...
docker --version
echo.

echo Step 2: Starting Services...
echo Starting Redis...
docker start redis 2>nul || docker run -d --name redis --network ai-agents-network -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

echo Starting MongoDB...
docker start mongodb 2>nul || docker run -d --name mongodb --network ai-agents-network -p 27017:27017 mongo:latest

echo Starting Retriever...
docker start retriever-redis-server 2>nul || echo Retriever not found - check setup

echo Starting Backend...
docker start backend-rag-full 2>nul || echo Backend not found - check setup

echo.
echo Step 3: Waiting for services to start...
timeout /t 10 /nobreak > nul

echo Step 4: Testing Services...
curl -s http://localhost:5008/v1/health_check
echo.
curl -s http://localhost:5007/v1/health_check
echo.

echo Step 5: Service Status...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo ===============================
echo Restart Complete!
echo ===============================
echo.
echo Your RAG system is ready:
echo - Backend: http://localhost:5008/docs
echo - Health: http://localhost:5008/v1/health_check
echo - Retriever: http://localhost:5007
echo - Redis: localhost:6379
echo - MongoDB: localhost:27017
echo.
