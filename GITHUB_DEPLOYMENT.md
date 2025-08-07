# 🚀 GitHub Deployment Instructions

Your ADF Monitor Pro web application is now ready for GitHub deployment!

## ✅ Deployment Status
- [x] GitHub Actions workflow configured
- [x] GitHub Codespaces ready
- [x] Docker configuration complete
- [x] Requirements file validated
- [x] Environment template created

## 🎯 Quick Deployment Steps

### 1. Create GitHub Repository
```bash
# Go to GitHub.com and create a new repository named "AIMS"
# Then run these commands:

git remote add origin https://github.com/SasidharPV/AIMS.git
git branch -M main
git push -u origin main
```

### 2. Enable GitHub Pages
1. Go to your repository → **Settings** → **Pages**
2. Under **Source**, select **GitHub Actions**
3. Your documentation site will be live at: `https://YOUR-USERNAME.github.io/AIMS`

### 3. Launch in Codespaces
1. Click the **"Code"** button on your repository
2. Select **"Create codespace on main"**
3. Wait for environment setup (2-3 minutes)
4. Run: `python startup.py webapp`
5. Access via the forwarded port 8501

## 🌟 Features Available

### 🤖 **AI-Powered Monitoring**
- Multi-AI provider support (OpenAI, Azure OpenAI, Google, Anthropic)
- Intelligent error analysis and retry recommendations
- Natural language insights for pipeline failures

### 📊 **Enterprise Dashboard**
- Professional Streamlit web interface
- Real-time Azure Data Factory monitoring
- Interactive charts and KPIs
- Historical analytics and trend analysis

### ⚙️ **Complete Admin Interface**
- **Azure Setup Tab**: Service principal configuration
- **AI Providers Tab**: Multi-provider AI configuration
- **Environments Tab**: Prod/Stage/Dev environment management
- **Notifications Tab**: Teams, Slack, Email, SMS alerts
- **Security Tab**: RBAC and audit logging

### 🌍 **Multi-Environment Support**
- Separate configurations for Production, Staging, Development
- Cross-environment monitoring and reporting
- Environment-specific alerting and notifications

### 🔔 **Smart Notifications**
- Multi-channel alerts (Teams, Slack, Email, SMS)
- Intelligent filtering and batching
- Custom notification templates
- Escalation rules for critical failures

### 🔒 **Enterprise Security**
- Service principal authentication
- Role-based access control
- Comprehensive audit logging
- Secure credential storage

## 📁 Repository Structure
```
AIMS/
├── webapp.py                    # Main Streamlit application
├── startup.py                   # Application launcher
├── requirements_webapp.txt      # Dependencies
├── .env.sample                  # Environment template
├── .devcontainer/               # Codespaces configuration
├── .github/workflows/           # CI/CD automation
├── Dockerfile                   # Container configuration
├── docker-compose.yml           # Multi-service deployment
└── UI_CONFIGURATION_DEMO.md     # Feature walkthrough
```

## 🔧 Configuration Guide

### Environment Variables (.env)
```bash
# Azure Configuration (Required)
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_SUBSCRIPTION_ID=your-subscription-id

# AI Providers (Optional - choose one or more)
OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-key
GOOGLE_API_KEY=your-google-key
ANTHROPIC_API_KEY=your-anthropic-key

# Notifications (Optional)
TEAMS_WEBHOOK_URL=your-teams-webhook
SLACK_WEBHOOK_URL=your-slack-webhook
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 🚀 Deployment Options

### GitHub Codespaces (Recommended)
- ☁️ Cloud-based development environment
- 🚀 No local setup required
- 🔧 Pre-configured Python environment
- 📊 Instant access to the web application

### Local Development
```bash
git clone https://github.com/SasidharPV/AIMS.git
cd AIMS
pip install -r requirements_webapp.txt
cp .env.sample .env
# Edit .env with your credentials
python startup.py webapp
```

### Docker Deployment
```bash
# Using Docker Compose
docker-compose up -d

# Or standalone Docker
docker build -t adf-monitor-pro .
docker run -p 8501:8501 --env-file .env adf-monitor-pro
```

### Azure Cloud Deployment
```bash
# Azure Container Instances
az container create \
  --resource-group myResourceGroup \
  --name adf-monitor-pro \
  --image your-registry/adf-monitor-pro:latest \
  --ports 8501

# Azure App Service
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name adf-monitor-pro \
  --runtime "PYTHON|3.11"
```

## 📞 Support & Community

- 🐛 **Issues**: [GitHub Issues](https://github.com/SasidharPV/AIMS/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/SasidharPV/AIMS/discussions)
- 📧 **Enterprise Support**: Contact for production deployments

## 🎉 Ready to Deploy!

Your ADF Monitor Pro is ready for GitHub! 

**Next steps:**
1. Push to GitHub: `git push origin main`
2. Enable GitHub Pages in repository settings
3. Launch in Codespaces to test
4. Share your deployment URL with your team!

**Live URLs will be:**
- 🌐 **Documentation**: `https://SasidharPV.github.io/AIMS`
- ☁️ **Live App**: Launch via GitHub Codespaces
- 🐳 **Container**: Deploy using Docker or Azure

---

**Made with ❤️ for the Azure Data Factory community**
