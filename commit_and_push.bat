@echo off
echo ============================================
echo   COMMIT AND PUSH CLEANED REPOSITORY
echo ============================================
echo.

echo 1. Adding our modified files (without external files)...
cd /d D:\ai-agents

git add CURRENT_STATE_FINAL.md
git add backup/20250715_160413/retriever_config.json
git add backup/RESTART_GUIDE_COMPLETE.md
git add backup/RESTART_GUIDE_FINAL.md
git add backup/SYSTEM_SAVE_STATE.md
git add backup/SYSTEM_STATE_SAVE.md
git add quick_restart.sh
git add restart_system_complete.sh
git add .gitignore
git add fix_git_scope.bat

echo.
echo 2. Checking what will be committed...
git status

echo.
echo 3. Committing changes...
git commit -m "Fix: Remove sensitive tokens and clean git repository scope"

echo.
echo 4. Pushing to GitHub...
git push origin master

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo   ✅ SUCCESS: Repository pushed to GitHub!
    echo ============================================
) else (
    echo.
    echo ============================================
    echo   ❌ FAILED: Push failed. Check error above.
    echo ============================================
)

echo.
pause
