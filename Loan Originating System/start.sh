#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}        LoanMatrix AI — Local Dev Server          ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ── Backend Setup ─────────────────────────────────
echo -e "${YELLOW}[1/4] Setting up Python backend...${NC}"

cd "$BACKEND_DIR"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install deps
source venv/bin/activate
echo "  Installing Python dependencies..."
pip install -q -r requirements.txt

# ── Frontend Setup ────────────────────────────────
echo -e "${YELLOW}[2/4] Setting up Node.js frontend...${NC}"

cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo "  Installing npm packages..."
    npm install
fi

# ── Start Servers ─────────────────────────────────
echo -e "${YELLOW}[3/4] Starting servers...${NC}"
echo ""

# Start backend
cd "$BACKEND_DIR"
source venv/bin/activate

echo -e "${GREEN}  Starting FastAPI backend on http://localhost:8000${NC}"
echo -e "  API Docs: http://localhost:8000/api/docs"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 2

# Start frontend
cd "$FRONTEND_DIR"
echo -e "${GREEN}  Starting React frontend on http://localhost:5173${NC}"
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  LoanMatrix AI is running!${NC}"
echo ""
echo -e "  🌐 Frontend:   http://localhost:5173"
echo -e "  🔧 Backend:    http://localhost:8000"
echo -e "  📚 API Docs:   http://localhost:8000/api/docs"
echo ""
echo -e "${YELLOW}  Press Ctrl+C to stop all servers${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Cleanup on Ctrl+C
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    # Kill any child processes
    pkill -P $BACKEND_PID 2>/dev/null || true
    pkill -P $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}All servers stopped. Goodbye!${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep script running
wait
