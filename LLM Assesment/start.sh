#!/bin/bash

echo "Starting LLM Assessment Agent..."
echo ""

# Start backend
echo "[1/2] Starting FastAPI backend..."
cd "$(dirname "$0")/backend"
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend
echo "[2/2] Starting Next.js frontend..."
cd "$(dirname "$0")/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "LLM Assessment Agent is running!"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
