#!/bin/bash
#
# Kilo Docs Sync Script
# 
# This script updates the local Kilo Code documentation mirror to the latest version.
# Run this periodically to keep your skill's references/ directory current.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="/Users/vinnygilberti/Downloads/untitled folder/kilocode"
REMOTE_URL="https://github.com/Kilo-Org/kilocode.git"

echo "🔄 Kilo Docs Sync"
echo "================="
echo ""

# Check if repo exists
if [ ! -d "$REPO_DIR/.git" ]; then
    echo "📦 Repository not found. Cloning fresh..."
    mkdir -p "$(dirname "$REPO_DIR")"
    git clone --depth 1 "$REMOTE_URL" "$REPO_DIR"
    echo "✅ Clone complete!"
else
    echo "📍 Repo found at: $REPO_DIR"
    echo "⬇️  Pulling latest changes..."
    cd "$REPO_DIR"
    
    # Fetch and check if there are updates
    git fetch origin
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/HEAD)
    
    if [ "$LOCAL" = "$REMOTE" ]; then
        echo "✅ Already up to date!"
    else
        git pull
        echo "✅ Updated to latest!"
        echo ""
        echo "📋 Recent changes:"
        git log --oneline -5
    fi
fi

echo ""
echo "📂 References symlink:"
ls -la "$SCRIPT_DIR/references"

echo ""
echo "📊 Documentation structure:"
find "$SCRIPT_DIR/references" -maxdepth 1 -type d | sort | head -20

echo ""
echo "🎉 Sync complete! Your skill now has the latest Kilo Code documentation."
