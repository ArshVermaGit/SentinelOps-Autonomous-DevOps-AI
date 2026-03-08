#!/bin/bash
set -e

echo "🛡️ Starting SentinelOps unified setup..."

# Check for prerequisites
command -v node >/dev/null 2>&1 || { echo >&2 "❌ Node.js is required but not installed. Aborting."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo >&2 "❌ Python 3 is required but not installed. Aborting."; exit 1; }

echo "📦 Installing root dependencies..."
npm install

echo "🎨 Setting up Frontend..."
cd sentinelops-frontend
if [ ! -f .env.local ]; then
    echo "📄 Creating .env.local from example..."
    cp .env.local.example .env.local
fi
npm install
cd ..

echo "⚙️ Setting up Backend..."
cd sentinelops-backend
if [ ! -f .env ]; then
    echo "📄 Creating .env from example..."
    cp .env.example .env
fi

# Check for venv or use system python if preferred
if [ ! -d .venv ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install black isort flake8 pytest

echo "✅ Setup complete! You are ready to develop."
echo "💡 Run 'make dev' to start the application."
