#!/bin/bash
# Stadium Dashboard - Quick Setup Script

echo "🏟️  Stadium Experience Dashboard - Quick Setup"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "\n${YELLOW}Step 1: Checking prerequisites...${NC}"

if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found. Please install Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python found: $(python --version)${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found. You can still test locally.${NC}"
else
    echo -e "${GREEN}✅ Docker found${NC}"
fi

if ! command -v gcloud &> /dev/null; then
    echo -e "${YELLOW}⚠️  gcloud not found. You won't be able to deploy to Cloud Run.${NC}"
else
    echo -e "${GREEN}✅ gcloud found${NC}"
fi

# Step 2: Create project structure
echo -e "\n${YELLOW}Step 2: Creating project structure...${NC}"
mkdir -p backend frontend
echo -e "${GREEN}✅ Directories created${NC}"

# Step 3: Setup backend
echo -e "\n${YELLOW}Step 3: Setting up backend...${NC}"
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Step 4: Quick test
echo -e "\n${YELLOW}Step 4: Testing backend (15 seconds)...${NC}"
timeout 15 python main.py &
sleep 5

if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is running!${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
fi

killall python 2>/dev/null || true

cd ..

# Step 5: Summary
echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Get your firebase-key.json from Firebase console"
echo "2. Place it in the backend folder"
echo "3. Run: cd backend && python main.py"
echo "4. Run: cd frontend && python -m http.server 3000"
echo "5. Open: http://localhost:3000"
echo ""
echo "For Cloud Run deployment, see SETUP_GUIDE.md"
