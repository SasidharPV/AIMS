#!/bin/bash

# ADF Monitor Pro - GitHub Repository Setup Script
# This script initializes your repository for GitHub deployment

set -e  # Exit on any error

echo "🏭 ADF Monitor Pro - GitHub Repository Setup"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_info "Initializing Git repository..."
    git init
    print_status "Git repository initialized"
else
    print_status "Git repository already exists"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    print_info "Creating .gitignore file..."
    cat > .gitignore << 'EOF'
# Environment files
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.venv
venv/
ENV/
env/

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# Backup files
backup/
*.bak

# Temporary files
temp/
tmp/
.tmp/

# OS files
.DS_Store
Thumbs.db

# Streamlit
.streamlit/secrets.toml

# Azure
.azure/
EOF
    print_status ".gitignore created"
else
    print_status ".gitignore already exists"
fi

# Create environment sample if it doesn't exist
if [ ! -f ".env.sample" ]; then
    print_info "Creating .env.sample file..."
    cat > .env.sample << 'EOF'
# Azure Configuration (Required)
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_SUBSCRIPTION_ID=your-subscription-id-here

# Azure Data Factory Configuration
AZURE_RESOURCE_GROUP=your-resource-group
AZURE_DATA_FACTORY_NAME=your-data-factory-name

# AI Provider Configuration (Choose one or more)
OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-key
GOOGLE_API_KEY=your-google-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Notification Configuration (Optional)
TEAMS_WEBHOOK_URL=your-teams-webhook-url
SLACK_WEBHOOK_URL=your-slack-webhook-url
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application Configuration
USE_MOCK_DATA=false
LOG_LEVEL=INFO
DEBUG_MODE=false
EOF
    print_status ".env.sample created"
else
    print_status ".env.sample already exists"
fi

# Check required files
print_info "Checking required files..."

required_files=(
    "webapp.py"
    "startup.py"
    "requirements_webapp.txt"
    ".github/workflows/deploy-webapp.yml"
    ".devcontainer/devcontainer.json"
    "Dockerfile"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "$file ✓"
    else
        print_warning "$file is missing"
    fi
done

# Add files to git
print_info "Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    print_info "No changes to commit"
else
    # Commit changes
    print_info "Committing changes..."
    git commit -m "🚀 Initial commit: ADF Monitor Pro web application

Features:
- 🤖 AI-powered pipeline monitoring
- 📊 Streamlit web dashboard  
- ⚙️ Complete admin configuration interface
- 🌍 Multi-environment support
- 🔔 Smart notifications
- 🔒 Enterprise security
- 🐳 Docker deployment ready
- 🌐 GitHub Codespaces integration"
    print_status "Changes committed"
fi

echo ""
echo "🎉 Repository setup complete!"
echo ""
print_info "Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Add your GitHub repository as remote:"
echo "   git remote add origin https://github.com/your-username/AIMS.git"
echo "3. Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo "4. Enable GitHub Pages in repository settings"
echo "5. Launch in Codespaces to test your deployment"
echo ""
print_info "🌐 Your app will be available at:"
echo "   • GitHub Pages: https://your-username.github.io/AIMS"
echo "   • Codespaces: Click 'Code' → 'Create codespace on main'"
echo ""
print_status "Happy deploying! 🚀"
