# Azure ADF Monitoring & AI Analysis - Quick Start Guide

## 🚀 **FASTEST PATH TO PRODUCTION**

You now have a complete enterprise-grade web application ready for real Azure integration. Follow these 3 simple steps:

### **⚡ Step 1: Automated Azure Setup (2 minutes)**
```powershell
# Run the automated setup script
python setup_azure_automated.py
```
**What this does:**
- ✅ Creates Azure service principal with Data Factory permissions
- ✅ Deploys Azure OpenAI with GPT-4 model
- ✅ Generates all configuration files (.env, config/*.yaml)
- ✅ Sets up resource group and permissions

### **⚡ Step 2: Validate Connections (30 seconds)**
```powershell
# Test Azure Data Factory connection
python test_adf_connection.py

# Test Azure OpenAI connection
python test_openai_connection.py
```

### **⚡ Step 3: Launch Enterprise Web App (10 seconds)**
```powershell
# Start the web application
python startup.py webapp
```
🌐 Open: http://localhost:8502

---

## 🎯 **WHAT YOU GET IMMEDIATELY**

### **📊 Enterprise Dashboard**
- Real-time ADF pipeline monitoring
- AI-powered failure analysis
- Cost tracking and optimization
- Multi-environment support

### **🧠 AI-Powered Analysis**
- Automatic error categorization
- Retry recommendations with confidence scores
- Root cause analysis
- Performance optimization suggestions

### **🏢 Enterprise Features**
- Multi-AI provider support (Azure OpenAI, OpenAI, Google, Anthropic)
- Environment management (Prod/Staging/Dev)
- Professional UI with modern styling
- Comprehensive logging and monitoring

### **🔒 Production Ready**
- Service principal authentication
- Secure credential management
- Docker containerization
- CI/CD pipeline support

---

## 🛠️ **MANUAL SETUP (If Automated Fails)**

<details>
<summary>Click to expand manual setup instructions</summary>

### 1. Azure Service Principal
```powershell
# Create service principal
az ad sp create-for-rbac --name "sp-adf-monitoring" --role "Data Factory Contributor"
```

### 2. Azure OpenAI Deployment
```powershell
# Create resource group
az group create --name "rg-adf-monitoring" --location "East US"

# Create Azure OpenAI
az cognitiveservices account create --name "openai-adf-monitoring" --resource-group "rg-adf-monitoring" --kind OpenAI --sku S0 --location "East US"

# Deploy GPT-4 model
az cognitiveservices account deployment create --name "openai-adf-monitoring" --resource-group "rg-adf-monitoring" --deployment-name "gpt-4-deployment" --model-name gpt-4 --model-version "0613"
```

### 3. Update .env File
```env
# Azure Service Principal
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Enable Azure Integration
USE_AZURE_OPENAI=true
ADF_MONITORING_ENABLED=true
```

</details>

---

## 🎮 **USING THE WEB APPLICATION**

### **📈 Dashboard Page**
- View all pipeline runs with status indicators
- See AI analysis results with confidence scores
- Monitor costs and performance metrics
- Filter by time range and status

### **⚠️ Failures Page** 
- Detailed failure analysis with AI insights
- Error categorization (transient/permanent/configuration)
- Retry recommendations with confidence levels
- Historical failure patterns

### **🔧 Actions Page**
- Execute pipeline actions (start/stop/retry)
- Bulk operations on multiple pipelines
- Schedule automated retries
- Custom action templates

### **📋 Logs Page**
- Real-time log streaming
- Advanced filtering and search
- Export logs to various formats
- Log analysis with AI summaries

### **⚙️ AI Configuration**
- Manage multiple AI providers
- Configure analysis parameters
- Test provider connections
- Monitor AI usage and costs

---

## 🔧 **CUSTOMIZATION & SCALING**

### **Adding New AI Providers**
Edit `config/ai_providers.yaml`:
```yaml
ai_providers:
  - provider_id: "google-gemini"
    provider_name: "Google Gemini Pro"
    model_name: "gemini-pro"
    api_key: "${GOOGLE_AI_API_KEY}"
    active: true
```

### **Environment Management**
Edit `config/environments.yaml`:
```yaml
environments:
  custom:
    name: "Custom Environment"
    azure_subscription_id: "different-subscription"
    monitoring_enabled: true
```

### **Docker Deployment**
```powershell
# Build and run with Docker
docker-compose up --build -d
```

### **Scaling for Enterprise**
- Deploy to Azure Container Instances
- Use Azure Key Vault for secrets
- Set up Azure Monitor integration
- Configure auto-scaling

---

## 🆘 **TROUBLESHOOTING**

### **Common Issues & Solutions**

❌ **"Azure CLI not found"**
```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI
# Or download from: https://aka.ms/installazurecliwindows
```

❌ **"OpenAI package not found"**
```powershell
pip install openai azure-identity azure-mgmt-datafactory streamlit plotly
```

❌ **"401 Unauthorized"**
- Check service principal credentials in .env
- Verify service principal has Data Factory Contributor role
- Ensure Azure OpenAI API key is correct

❌ **"Model deployment not found"**
- Check deployment name in Azure portal
- Verify model is deployed and active
- Wait a few minutes after deployment

### **Getting Help**
1. Run diagnostics: `python test_adf_connection.py`
2. Check logs in the web app's Logs section
3. Validate configuration in AI Config section
4. Review Azure portal for resource status

---

## 🎯 **SUCCESS CRITERIA**

You'll know everything is working when:
- ✅ Web app loads at http://localhost:8502
- ✅ Dashboard shows your ADF pipelines
- ✅ AI analysis provides insights on failures
- ✅ All test scripts pass validation
- ✅ No errors in the application logs

## 🚀 **GO LIVE!**

Your enterprise ADF monitoring solution is now ready for production use! 

**Total setup time: ~5 minutes**

**What's monitoring:** All your Azure Data Factory pipelines across subscriptions

**AI Analysis:** Real-time failure analysis with actionable insights

**Enterprise Features:** Multi-environment, multi-provider, professional UI

---

*Questions? Run the test scripts or check the troubleshooting section above.*
