@echo off
echo ===============================
echo RAG System Save State
echo ===============================
echo Date: %date% %time%
echo.

echo Step 1: System Status Check...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo Step 2: Testing Services...
curl -s http://localhost:5008/v1/health_check
echo.
curl -s http://localhost:5007/v1/health_check
echo.

echo Step 3: Current Working Directory...
echo %CD%
echo.

echo Step 4: Git Status...
git status
echo.

echo ===============================
echo Save State Complete!
echo ===============================
echo.
echo Your system is ready to resume from:
echo - Backend: http://localhost:5008/docs
echo - Retriever: http://localhost:5007
echo - Redis: localhost:6379
echo - MongoDB: localhost:27017
echo.
echo To restart after shutdown:
echo 1. cd D:\ai-agents
echo 2. call restart_system.bat
echo 3. call test_system.bat
echo.
