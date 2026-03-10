#!/bin/bash

# TuneTrace.AI Web Launcher
# This script starts both backend and frontend servers

set -e

echo "🎵 TuneTrace.AI Web Launcher"
echo "=============================="
echo ""

# Load API key from .env file if it exists
if [ -f ".env" ]; then
    echo "📄 Loading configuration from .env file..."
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    echo ""
fi

# Check for Google API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY not found"
    echo ""
    echo "Please add it to the .env file or set it with:"
    echo "  export GOOGLE_API_KEY='your-api-key-here'"
    echo ""
    echo "Get your key from: https://aistudio.google.com/app/apikey"
    exit 1
fi

echo "✅ Google API Key found"
echo ""

# Check if dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend && npm install && cd ..
    echo ""
fi

echo "🚀 Starting TuneTrace.AI..."
echo ""
echo "Backend will be available at: http://localhost:8000"
echo "Frontend will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""
echo "=========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Start backend
cd app
python main.py &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID


