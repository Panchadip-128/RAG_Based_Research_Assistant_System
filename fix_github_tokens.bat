@echo off
echo ===============================
echo GitHub Push Protection Fix
echo ===============================
echo.
echo GitHub detected Hugging Face tokens in files. Let's clean them up.
echo.
echo Files with tokens:
echo - RESTART_GUIDE_COMPLETE.md
echo - RESTART_GUIDE_FINAL.md  
echo - SYSTEM_SAVE_STATE.md
echo - SYSTEM_STATE_SAVE.md
echo.
echo Step 1: Removing sensitive tokens...

REM Create backup directory
if not exist backup mkdir backup

REM Backup original files
copy RESTART_GUIDE_COMPLETE.md backup\ 2>nul
copy RESTART_GUIDE_FINAL.md backup\ 2>nul
copy SYSTEM_SAVE_STATE.md backup\ 2>nul
copy SYSTEM_STATE_SAVE.md backup\ 2>nul

echo Backups created in backup\ folder
echo.

echo Step 2: Cleaning tokens from files...

REM Remove lines containing tokens (this is a simplified approach)
findstr /v "hf_" RESTART_GUIDE_COMPLETE.md > temp_restart_complete.md 2>nul
findstr /v "hf_" RESTART_GUIDE_FINAL.md > temp_restart_final.md 2>nul
findstr /v "hf_" SYSTEM_SAVE_STATE.md > temp_save_state.md 2>nul
findstr /v "hf_" SYSTEM_STATE_SAVE.md > temp_state_save.md 2>nul

REM Replace original files with cleaned versions
move temp_restart_complete.md RESTART_GUIDE_COMPLETE.md 2>nul
move temp_restart_final.md RESTART_GUIDE_FINAL.md 2>nul
move temp_save_state.md SYSTEM_SAVE_STATE.md 2>nul
move temp_state_save.md SYSTEM_STATE_SAVE.md 2>nul

echo Tokens removed from files
echo.

echo Step 3: Current system status...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo Step 4: Git status...
git status
echo.

echo ===============================
echo Cleanup Complete!
echo ===============================
echo.
echo Next steps:
echo 1. git add .
echo 2. git commit -m "Fix: Remove sensitive tokens from documentation"
echo 3. git push origin master
echo.
echo Your RAG system is still running and ready!
echo - Backend: http://localhost:5008/docs
echo - Health: http://localhost:5008/v1/health_check
echo.
