#!/bin/bash

echo "🚀 Initial Server Setup for Bethel Prayer Ministry"
echo "📅 $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVER_IP="91.99.232.214"
GIT_REPO="https://github.com/Boateng555/bethel2.git"
PROJECT_DIR="/home/cyberpanel/public_html/bethel"

echo -e "${YELLOW}🔧 Step 1: Setting up project directory...${NC}"
ssh root@$SERVER_IP << 'EOF'
# Create project directory
mkdir -p /home/cyberpanel/public_html/bethel
cd /home/cyberpanel/public_html/bethel

# Clone the repository
git clone https://github.com/Boateng555/bethel2.git .
echo "✅ Repository cloned successfully"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create necessary directories
mkdir -p staticfiles media logs
echo "✅ Directories created"

# Set permissions
chown -R cyberpanel:cyberpanel /home/cyberpanel/public_html/bethel
chmod -R 755 /home/cyberpanel/public_html/bethel
echo "✅ Permissions set"
EOF

echo -e "${GREEN}✅ Initial server setup completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Set up PostgreSQL database"
echo "2. Run the deployment script: ./deploy_production.sh" 