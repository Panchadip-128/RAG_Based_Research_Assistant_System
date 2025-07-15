@echo off
echo ============================================
echo   ALTERNATIVE: FRESH REPOSITORY SETUP
echo ============================================
echo.

echo This creates a completely clean repository without any history.
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" exit /b

cd /d D:\ai-agents

echo.
echo 1. Backing up current .git folder...
if exist .git_backup rmdir /s /q .git_backup
move .git .git_backup

echo.
echo 2. Initializing fresh repository...
git init
git branch -m master

echo.
echo 3. Adding clean files...
git add .
git commit -m "Initial commit: Clean RAG system without sensitive tokens"

echo.
echo 4. Adding GitHub remote...
git remote add origin https://github.com/Panchadip-128/opea.git

echo.
echo 5. Force pushing to GitHub (this will overwrite history)...
git push -u origin master --force

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo   ✅ SUCCESS: Fresh repository created!
    echo ============================================
    echo.
    echo The old .git folder is saved as .git_backup
    echo You can delete it if everything works correctly.
) else (
    echo.
    echo ============================================
    echo   ❌ FAILED: Restoring original .git folder
    echo ============================================
    if exist .git rmdir /s /q .git
    move .git_backup .git
)

echo.
pause
