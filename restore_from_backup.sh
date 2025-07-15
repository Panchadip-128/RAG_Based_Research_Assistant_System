#!/bin/bash
echo "🔄 RESTORING FROM BACKUP"
echo "======================="

# Find latest backup
LATEST_BACKUP=$(find backup -type d -name "????????_??????" | sort | tail -1)
if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ No backup found!"
    exit 1
fi

echo "📁 Latest backup: $LATEST_BACKUP"

# Show backup contents
echo "📊 Backup contents:"
cat $LATEST_BACKUP/SAVE_SUMMARY.md

# Restore containers (manual step)
echo "🔧 To restore containers, run:"
echo "   ./restart_system_complete.sh"
echo "   python3 visual_test_rag.py"
