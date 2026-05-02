#!/bin/bash
# Quick Start Script for jPOS CMS Phase 1 Authentication

set -e

echo "🚀 jPOS CMS Phase 1 Authentication - Quick Start"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}[1/5]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $(python3 --version | cut -d' ' -f2) found"

# Setup Backend
echo ""
echo -e "${BLUE}[2/5]${NC} Setting up backend..."
cd backend

# Create .env if not exists
if [ ! -f .env ]; then
    echo "   Creating .env from .env.example..."
    cp .env.example .env
fi
echo -e "${GREEN}✓${NC} Backend configured"

# Initialize Database
echo ""
echo -e "${BLUE}[3/5]${NC} Initializing database..."
python3 migrate.py
echo -e "${GREEN}✓${NC} Database ready"

# Setup Frontend
echo ""
echo -e "${BLUE}[4/5]${NC} Setting up frontend..."
cd ../frontend
if [ ! -d node_modules ]; then
    echo "   Installing dependencies..."
    npm install --silent
fi
echo -e "${GREEN}✓${NC} Frontend ready"

# Ready!
echo ""
echo -e "${BLUE}[5/5]${NC} Setup complete!"
echo ""
echo -e "${GREEN}=================================================="
echo "✅ ALL SYSTEMS READY!"
echo "==================================================${NC}"
echo ""
echo -e "${YELLOW}Starting Services:${NC}"
echo ""
echo "Backend (Terminal 1):"
echo "  $ cd backend && python3 run.py"
echo "  → API: http://localhost:8000"
echo "  → Docs: http://localhost:8000/docs"
echo ""
echo "Frontend (Terminal 2):"
echo "  $ cd frontend && npm run dev"
echo "  → App: http://localhost:5173"
echo ""
echo -e "${YELLOW}Test Credentials:${NC}"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo -e "${YELLOW}Quick Test:${NC}"
echo "  1. Open http://localhost:5173"
echo "  2. Login with admin/admin123"
echo "  3. Check /api/docs for endpoint testing"
echo "  4. Run tests: cd backend && pytest tests/test_auth_phase1.py -v"
echo ""
