#!/bin/bash
# ================================
# ZeroTrust AI — One Command Startup
# ================================

echo "🛡️  Starting ZeroTrust AI..."

# Train models if not already trained
if [ ! -f "backend/ml/models/xgboost_clf.pkl" ]; then
  echo "🤖 Training ML models (first time only ~2 mins)..."
  cd backend && python ml/train.py && cd ..
fi

# Start backend
echo "⚡ Starting FastAPI backend on port 8000..."
cd backend && uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
sleep 3

# Start frontend
echo "🌐 Starting Next.js frontend on port 3000..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ ZeroTrust AI is running!"
echo "   Dashboard → http://localhost:3000"
echo "   API Docs  → http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop everything"

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
