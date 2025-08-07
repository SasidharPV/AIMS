# 🚀 ADF Monitor Pro - GitHub Deployment Guide

[![Deploy to GitHub Pages](https://github.com/your-username/AIMS/actions/workflows/deploy-webapp.yml/badge.svg)](https://github.com/your-username/AIMS/actions/workflows/deploy-webapp.yml)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/your-username/AIMS)

**Deploy your ADF Monitor Pro web application to GitHub in minutes!**

## 🌐 Deployment Options

### 1. GitHub Codespaces (Recommended) ⭐

**Perfect for instant cloud deployment and testing:**

1. Click the **"Code"** button above
2. Select **"Create codespace on main"**
3. Wait for environment setup (2-3 minutes)
4. Run: `python startup.py webapp`
5. Access via forwarded port 8501

**✅ Benefits:**
- ☁️ Runs in the cloud
- 🚀 No local setup required
- 🔧 Pre-configured environment
- 💻 Access from any device
- 🔗 Shareable URLs

### 2. GitHub Pages

**Static documentation and project showcase:**

- **Live Demo**: [Your ADF Monitor Pro](https://your-username.github.io/AIMS)
- **Automatic Deployment**: Updates on every push to main
- **Professional Landing Page**: Feature showcase and quick start guide

### 3. Local Development

**For customization and development:**

```bash
git clone https://github.com/your-username/AIMS.git
cd AIMS
pip install -r requirements_webapp.txt
python startup.py webapp
```

## 🛠️ Setup Your Repository

### Step 1: Fork or Create Repository

1. **Fork this repository** or **create a new one**
2. **Clone to your local machine**:
   ```bash
   git clone https://github.com/your-username/AIMS.git
   cd AIMS
   ```

### Step 2: Enable GitHub Pages

1. Go to **Settings** → **Pages**
2. Select **Source**: GitHub Actions
3. Your documentation site will be available at: `https://your-username.github.io/AIMS`

### Step 3: Enable Codespaces

Codespaces are automatically enabled with the `.devcontainer/devcontainer.json` configuration.

### Step 4: Configure Secrets (Optional)

For production deployment, add these secrets in **Settings** → **Secrets and variables** → **Actions**:

```
AZURE_TENANT_ID
AZURE_CLIENT_ID
AZURE_CLIENT_SECRET
AZURE_SUBSCRIPTION_ID
OPENAI_API_KEY
```

## 📋 Repository Checklist

Make sure your repository has these files:

- ✅ `.github/workflows/deploy-webapp.yml` - CI/CD pipeline
- ✅ `.devcontainer/devcontainer.json` - Codespaces configuration  
- ✅ `requirements_webapp.txt` - Python dependencies
- ✅ `webapp.py` - Main Streamlit application
- ✅ `startup.py` - Application launcher
- ✅ `.env.sample` - Environment template
- ✅ `README.md` - Project documentation

## 🚀 Quick Commands

### Launch in Codespaces
```bash
# After Codespaces opens:
python startup.py webapp
```

### Local Development
```bash
# Install dependencies
pip install -r requirements_webapp.txt

# Copy environment template
cp .env.sample .env

# Edit with your credentials
nano .env

# Launch application
python startup.py webapp
```

### Docker Deployment
```bash
# Build image
docker build -t adf-monitor-pro .

# Run container
docker run -p 8501:8501 --env-file .env adf-monitor-pro
```

## 🌟 Features Showcase

### 🤖 **AI-Powered Analysis**
Multiple AI providers for intelligent error analysis

### 📊 **Enterprise Dashboard** 
Professional Streamlit web interface

### ⚙️ **Admin Configuration**
Complete UI-based setup (no config files!)

### 🌍 **Multi-Environment**
Prod/Stage/Dev monitoring

### 🔔 **Smart Notifications**
Teams, Slack, Email, SMS alerts

### 🔒 **Enterprise Security**
RBAC and audit logging

## 🔗 Quick Links

- **Live Demo**: [GitHub Pages Site](https://your-username.github.io/AIMS)
- **Launch App**: [GitHub Codespaces](https://codespaces.new/your-username/AIMS)
- **Issues**: [Report Bug](https://github.com/your-username/AIMS/issues)
- **Discussions**: [Get Help](https://github.com/your-username/AIMS/discussions)

## 📞 Support

- 💬 **GitHub Discussions** for questions
- 🐛 **GitHub Issues** for bugs
- 📧 **Email Support** for enterprise inquiries

---

**🎉 Ready to deploy? Click the Codespaces button above to get started!**
