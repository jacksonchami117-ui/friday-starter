#!/bin/bash

echo "🚀 FRIDAY STARTER QUICK VERIFICATION"
echo "===================================="

# Check current directory
CURRENT_DIR=$(pwd)
echo "📍 Current directory: $CURRENT_DIR"

# Expected directory
EXPECTED_DIR="/Users/jacksonn/Documents/GitHub/friday-starter"

if [[ "$CURRENT_DIR" == "$EXPECTED_DIR" ]]; then
    echo "✅ CORRECT LOCATION"
else
    echo "❌ WRONG LOCATION!"
    echo "   Expected: $EXPECTED_DIR"
    echo "   Current:  $CURRENT_DIR"
    echo ""
    echo "🔧 FIX: Run: cd ~/Documents/GitHub/friday-starter"
    exit 1
fi

echo ""
echo "🔍 Checking project files..."

# Check key files
FILES=("app.py" "Dockerfile" "requirements.txt" ".github/workflows/deploy_apprunner.yml")
ALL_GOOD=true

for file in "${FILES[@]}"; do
    if [ -e "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (MISSING)"
        ALL_GOOD=false
    fi
done

echo ""
if [ "$ALL_GOOD" = true ]; then
    echo "🎉 SUCCESS: You're in the correct Friday Starter workspace!"
    echo "🚀 Ready to proceed with deployments and automation."
else
    echo "⚠️  Some files are missing. Check the project structure."
fi

echo ""
echo "🔐 GitHub Token: [Retrieve from user when needed]"
echo "🌐 Repository: jacksonchami117-ui/friday-starter"
echo "☁️  AWS Region: ap-southeast-2"
