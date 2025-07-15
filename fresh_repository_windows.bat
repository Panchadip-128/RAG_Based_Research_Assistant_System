@echo off
echo ============================================
echo   WINDOWS-COMPATIBLE FRESH REPOSITORY
echo ============================================
echo.

echo This will create a completely clean repository without any history.
echo This is the safest approach for Windows CMD.
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" exit /b

cd /d D:\ai-agents

echo.
echo 1. Backing up current .git folder...
if exist .git_backup rmdir /s /q .git_backup
move .git .git_backup

echo.
echo 2. Creating final cleanup of any remaining tokens...
powershell -Command "(Get-Content 'backup\RESTART_GUIDE_COMPLETE.md') -replace 'hf_[A-Za-z0-9_]+', 'YOUR_HUGGINGFACE_TOKEN' | Set-Content 'backup\RESTART_GUIDE_COMPLETE.md'"
powershell -Command "(Get-Content 'backup\RESTART_GUIDE_FINAL.md') -replace 'hf_[A-Za-z0-9_]+', 'YOUR_HUGGINGFACE_TOKEN' | Set-Content 'backup\RESTART_GUIDE_FINAL.md'"
powershell -Command "(Get-Content 'backup\SYSTEM_SAVE_STATE.md') -replace 'hf_[A-Za-z0-9_]+', 'YOUR_HUGGINGFACE_TOKEN' | Set-Content 'backup\SYSTEM_SAVE_STATE.md'"
powershell -Command "(Get-Content 'backup\SYSTEM_STATE_SAVE.md') -replace 'hf_[A-Za-z0-9_]+', 'YOUR_HUGGINGFACE_TOKEN' | Set-Content 'backup\SYSTEM_STATE_SAVE.md'"
powershell -Command "(Get-Content 'backup\20250715_160413\retriever_config.json') -replace 'hf_[A-Za-z0-9_]+', 'YOUR_HUGGINGFACE_TOKEN' | Set-Content 'backup\20250715_160413\retriever_config.json'"

echo.
echo 3. Initializing fresh repository...
git init
git branch -m master

echo.
echo 4. Creating comprehensive .gitignore...
(
echo # Ignore sensitive files
echo **/*token*
echo **/*secret*
echo **/*key*
echo **/*password*
echo.
echo # Ignore system files
echo **/$RECYCLE.BIN/
echo **/System Volume Information/
echo **/WindowsApps/
echo **/*.tmp
echo **/__pycache__/
echo **/.vscode/
echo **/node_modules/
echo.
echo # Ignore parent directory files
echo ../
echo.
echo # Keep only project files
echo !*.py
echo !*.md
echo !*.txt
echo !*.yaml
echo !*.yml
echo !*.json
echo !*.sh
echo !*.bat
echo !assets/
echo !comps/
echo !design-patterns/
echo !install/
echo !backup/
) > .gitignore

echo.
echo 5. Adding clean files...
git add .
git commit -m "Initial commit: Clean RAG system - tokens removed"

echo.
echo 6. Adding GitHub remote...
git remote add origin https://github.com/Panchadip-128/opea.git

echo.
echo 7. Force pushing to GitHub (this will overwrite history)...
git push -u origin master --force

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo   ✅ SUCCESS: Fresh repository created!
    echo ============================================
    echo.
    echo Your RAG system is now on GitHub with clean history.
    echo The old .git folder is saved as .git_backup
    echo.
    echo Next steps:
    echo   1. Test your system: test_system.bat
    echo   2. Continue development from clean state
    echo   3. Delete .git_backup if everything works
    echo.
) else (
    echo.
    echo ============================================
    echo   ❌ FAILED: Restoring original .git folder
    echo ============================================
    if exist .git rmdir /s /q .git
    move .git_backup .git
    echo.
    echo Alternative: Manually create new GitHub repository
    echo   1. Go to GitHub and delete the current repository
    echo   2. Create a new repository with same name
    echo   3. Run this script again
)

echo.
pause
