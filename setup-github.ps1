# ADF Monitor Pro - GitHub Repository Setup Script (PowerShell)
# This script initializes your repository for GitHub deployment

param(
    [switch]$SkipConfirmation
)

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green" 
    Yellow = "Yellow"
    Blue = "Blue"
    White = "White"
}

function Write-Status {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Colors.Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $Colors.Blue
}

Write-Host "🏭 ADF Monitor Pro - GitHub Repository Setup" -ForegroundColor $Colors.White
Write-Host "==============================================" -ForegroundColor $Colors.White
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Status "Git is installed: $gitVersion"
} catch {
    Write-Error "Git is not installed. Please install Git first."
    exit 1
}

# Check if we're in a git repository
if (!(Test-Path ".git")) {
    Write-Info "Initializing Git repository..."
    git init
    Write-Status "Git repository initialized"
} else {
    Write-Status "Git repository already exists"
}

# Create .gitignore if it doesn't exist
if (!(Test-Path ".gitignore")) {
    Write-Info "Creating .gitignore file..."
    $gitignoreContent = @"
# Environment files
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*`$py.class
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
"@
    Set-Content -Path ".gitignore" -Value $gitignoreContent
    Write-Status ".gitignore created"
} else {
    Write-Status ".gitignore already exists"
}

# Create environment sample if it doesn't exist
if (!(Test-Path ".env.sample")) {
    Write-Info "Creating .env.sample file..."
    $envSampleContent = @"
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
"@
    Set-Content -Path ".env.sample" -Value $envSampleContent
    Write-Status ".env.sample created"
} else {
    Write-Status ".env.sample already exists"
}

# Check required files
Write-Info "Checking required files..."

$requiredFiles = @(
    "webapp.py",
    "startup.py", 
    "requirements_webapp.txt",
    ".github\workflows\deploy-webapp.yml",
    ".devcontainer\devcontainer.json",
    "Dockerfile"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Status "$file ✓"
    } else {
        Write-Warning "$file is missing"
    }
}

# Add files to git
Write-Info "Adding files to git..."
git add .

# Check if there are changes to commit
$gitStatus = git status --porcelain
if ([string]::IsNullOrEmpty($gitStatus)) {
    Write-Info "No changes to commit"
} else {
    # Commit changes
    Write-Info "Committing changes..."
    $commitMessage = @"
🚀 Initial commit: ADF Monitor Pro web application

Features:
- 🤖 AI-powered pipeline monitoring
- 📊 Streamlit web dashboard  
- ⚙️ Complete admin configuration interface
- 🌍 Multi-environment support
- 🔔 Smart notifications
- 🔒 Enterprise security
- 🐳 Docker deployment ready
- 🌐 GitHub Codespaces integration
"@
    git commit -m $commitMessage
    Write-Status "Changes committed"
}

Write-Host ""
Write-Host "🎉 Repository setup complete!" -ForegroundColor $Colors.Green
Write-Host ""
Write-Info "Next steps:"
Write-Host "1. Create a new repository on GitHub"
Write-Host "2. Add your GitHub repository as remote:"
Write-Host "   git remote add origin https://github.com/your-username/AIMS.git"
Write-Host "3. Push to GitHub:"
Write-Host "   git branch -M main"
Write-Host "   git push -u origin main"
Write-Host "4. Enable GitHub Pages in repository settings"
Write-Host "5. Launch in Codespaces to test your deployment"
Write-Host ""
Write-Info "🌐 Your app will be available at:"
Write-Host "   • GitHub Pages: https://your-username.github.io/AIMS"
Write-Host "   • Codespaces: Click 'Code' → 'Create codespace on main'"
Write-Host ""
Write-Status "Happy deploying! 🚀"

if (!$SkipConfirmation) {
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor $Colors.Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
