#!/bin/bash
# MCP Task Server Runner Script

set -e

echo "🚀 Starting MCP Task Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if database is running
if ! sudo docker-compose ps | grep -q "Up"; then
    echo "🐘 Starting PostgreSQL database..."
    sudo docker-compose up -d
    echo "⏳ Waiting for database to be ready..."
    sleep 10
fi

# Set Python path
export PYTHONPATH=/home/sanzad/git/mcp

# Run the server
echo "✅ Starting MCP server..."
python main.py
