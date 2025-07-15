@echo off
echo ============================================
echo   REMOVE TOKENS FROM GIT HISTORY
echo ============================================
echo.

echo WARNING: This will rewrite git history. Make sure you have a backup!
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" exit /b

cd /d D:\ai-agents

echo.
echo 1. Creating backup of current state...
git branch backup-before-cleanup

echo.
echo 2. Using git filter-branch to remove tokens from all commits...
git filter-branch --tree-filter "find . -type f -name '*.md' -exec sed -i 's/hf_[A-Za-z0-9_]\{1,\}/YOUR_HUGGINGFACE_TOKEN/g' {} \;" --all

echo.
echo 3. Force update the origin...
git push origin --force --all

echo.
echo 4. Cleaning up...
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d
git reflog expire --expire=now --all
git gc --prune=now

echo.
echo ============================================
echo   HISTORY CLEANUP COMPLETE
echo ============================================
echo.
echo If this fails, try the alternative approach:
echo   1. Delete the repository on GitHub
echo   2. Create a new repository
echo   3. Push clean code to new repository
echo.
pause
