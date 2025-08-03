# ADF Monitor Pro - Deployment Guide

## 🎯 Overview

ADF Monitor Pro is an enterprise-grade web application for monitoring and automating Azure Data Factory pipelines across multiple environments with AI-powered error analysis and intelligent automation.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ADF Monitor Pro Architecture                  │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (Streamlit Web App)                                   │
│  ├── Dashboard & Monitoring Views                               │
│  ├── Configuration Management                                   │
│  ├── Real-time Analytics & Charts                              │
│  └── Interactive Control Panel                                  │
├─────────────────────────────────────────────────────────────────┤
│  Backend Services                                               │
│  ├── Multi-Environment ADF Clients                             │
│  ├── Enterprise AI Manager (Multi-Provider)                    │
│  ├── Intelligent Action Engine                                 │
│  ├── Multi-Channel Notification Service                        │
│  └── Comprehensive Audit & Logging                             │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                     │
│  ├── SQLite/PostgreSQL Database                                │
│  ├── Configuration Management (YAML)                           │
│  ├── Environment-Specific Settings                             │
│  └── AI Provider Configurations                                │
├─────────────────────────────────────────────────────────────────┤
│  External Integrations                                          │
│  ├── Azure Data Factory REST APIs                              │
│  ├── Multiple AI Providers (OpenAI, Azure OpenAI, etc.)       │
│  ├── Azure Monitor & Application Insights                      │
│  └── Notification Channels (Teams, Slack, Email)              │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Method 1: Using Startup Script (Recommended)

```bash
# 1. Clone and navigate to the project
cd /path/to/adf-monitor-pro

# 2. Run initial setup
python startup.py setup

# 3. Configure credentials (see Configuration section)
cp .env.sample .env
# Edit .env with your credentials

# 4. Launch the web application
python startup.py webapp

# 5. Access at http://localhost:8501
```

### Method 2: Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements_webapp.txt

# 2. Initialize configuration
python -c "from enterprise_config import get_config_manager; get_config_manager()"

# 3. Configure environment
cp .env.sample .env
# Edit .env file

# 4. Launch application
streamlit run webapp.py --server.port 8501
```

## ⚙️ Configuration

### 1. Environment Variables (.env)

```bash
# Azure Configuration
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_SUBSCRIPTION_ID=your-subscription-id-here

# AI Providers
OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
GOOGLE_AI_API_KEY=your-google-api-key

# Notifications
TEAMS_WEBHOOK_URL=https://your-teams-webhook-url
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-app-password
```

### 2. Environment Configuration (config/environments.yaml)

```yaml
environments:
  - name: "Production"
    subscription_id: "prod-subscription-id"
    resource_group: "prod-rg-adf"
    data_factory: "prod-adf-main"
    region: "eastus"
    tenant_id: "your-tenant-id"
    client_id: "your-client-id"
    client_secret: "your-client-secret"
    status: "Active"
    polling_interval: 300
    retry_attempts: 3
```

### 3. AI Provider Configuration (config/ai_providers.yaml)

```yaml
ai_providers:
  - provider_id: "openai-gpt4"
    provider_name: "OpenAI GPT-4"
    model_name: "gpt-4"
    api_endpoint: "https://api.openai.com/v1/chat/completions"
    api_key: "your-openai-api-key"
    temperature: 0.3
    max_tokens: 1000
    confidence_threshold: 75
    active: true
    cost_per_1k_tokens: 0.03
```

## 🏢 Enterprise Deployment Options

### Option 1: Azure Container Instance (Recommended)

```bash
# 1. Create container image
docker build -t adf-monitor-pro .

# 2. Push to Azure Container Registry
az acr build --registry myregistry --image adf-monitor-pro .

# 3. Deploy to Azure Container Instance
az container create \
  --resource-group myResourceGroup \
  --name adf-monitor-pro \
  --image myregistry.azurecr.io/adf-monitor-pro:latest \
  --ports 8501 \
  --environment-variables \
    AZURE_TENANT_ID=$AZURE_TENANT_ID \
    AZURE_CLIENT_ID=$AZURE_CLIENT_ID \
    OPENAI_API_KEY=$OPENAI_API_KEY
```

### Option 2: Azure App Service

```bash
# 1. Create App Service Plan
az appservice plan create \
  --resource-group myResourceGroup \
  --name adf-monitor-plan \
  --sku B1 \
  --is-linux

# 2. Create Web App
az webapp create \
  --resource-group myResourceGroup \
  --plan adf-monitor-plan \
  --name adf-monitor-pro \
  --deployment-container-image-name adf-monitor-pro:latest

# 3. Configure environment variables
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name adf-monitor-pro \
  --settings \
    AZURE_TENANT_ID=$AZURE_TENANT_ID \
    AZURE_CLIENT_ID=$AZURE_CLIENT_ID
```

### Option 3: Azure Kubernetes Service (AKS)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adf-monitor-pro
spec:
  replicas: 2
  selector:
    matchLabels:
      app: adf-monitor-pro
  template:
    metadata:
      labels:
        app: adf-monitor-pro
    spec:
      containers:
      - name: adf-monitor-pro
        image: myregistry.azurecr.io/adf-monitor-pro:latest
        ports:
        - containerPort: 8501
        env:
        - name: AZURE_TENANT_ID
          valueFrom:
            secretKeyRef:
              name: azure-secrets
              key: tenant-id
```

### Option 4: On-Premises Deployment

```bash
# 1. Set up Python environment
python -m venv adf_monitor_env
source adf_monitor_env/bin/activate  # Linux/Mac
# or
adf_monitor_env\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements_webapp.txt

# 3. Configure environment
cp .env.sample .env
# Edit .env with your settings

# 4. Set up as a service (systemd example)
sudo cp adf-monitor-pro.service /etc/systemd/system/
sudo systemctl enable adf-monitor-pro
sudo systemctl start adf-monitor-pro
```

## 🔒 Security Configuration

### 1. Authentication Setup

```python
# Enable authentication in system config
system:
  security:
    enable_authentication: true
    enable_rbac: true
    password_policy:
      min_length: 8
      require_uppercase: true
      require_numbers: true
```

### 2. Azure Service Principal Setup

```bash
# Create service principal for ADF access
az ad sp create-for-rbac \
  --name "adf-monitor-pro" \
  --role "Data Factory Contributor" \
  --scopes "/subscriptions/{subscription-id}/resourceGroups/{rg-name}"

# Note the output for environment configuration
```

### 3. Network Security

```bash
# Configure firewall rules (if needed)
az network nsg rule create \
  --resource-group myResourceGroup \
  --nsg-name myNetworkSecurityGroup \
  --name AllowADFMonitor \
  --protocol Tcp \
  --priority 1000 \
  --destination-port-range 8501 \
  --access Allow
```

## 📊 Monitoring & Observability

### 1. Application Insights Integration

```python
# Configure Application Insights
APPINSIGHTS_INSTRUMENTATIONKEY=your-instrumentation-key
APPINSIGHTS_CONNECTION_STRING=your-connection-string
```

### 2. Health Checks

The application includes built-in health checks accessible at:
- `http://localhost:8501/health` - Basic health status
- `http://localhost:8501/metrics` - Prometheus metrics

### 3. Logging Configuration

```yaml
# Configure in system config
system:
  log_level: INFO
  log_file: logs/adf_monitor.log
  enable_audit_trail: true
  monitoring:
    enable_health_checks: true
    enable_metrics_collection: true
```

## 🔄 Backup & Recovery

### 1. Database Backup

```bash
# SQLite backup
cp adf_monitor_enterprise.db backup/adf_monitor_$(date +%Y%m%d).db

# PostgreSQL backup (if using PostgreSQL)
pg_dump adf_monitor_db > backup/adf_monitor_$(date +%Y%m%d).sql
```

### 2. Configuration Backup

```bash
# Export all configurations
python -c "
from enterprise_config import get_config_manager
config_manager = get_config_manager()
config_manager.export_configuration('backup/config_$(date +%Y%m%d).yaml')
"
```

## 🎛️ Management Commands

### Application Management

```bash
# Start application
python startup.py webapp

# Run demonstrations
python startup.py demo

# Run system tests
python startup.py test

# Initial setup
python startup.py setup
```

### Configuration Management

```bash
# Export configuration
python -c "from enterprise_config import get_config_manager; get_config_manager().export_configuration('config_backup.yaml')"

# Import configuration
python -c "from enterprise_config import get_config_manager; get_config_manager().import_configuration('config_backup.yaml')"
```

### Database Management

```bash
# View database stats
python -c "from database import db_manager; print(db_manager.get_dashboard_stats())"

# Clean old records
python -c "from database import db_manager; db_manager.cleanup_old_records(days=30)"
```

## 🔧 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   python startup.py webapp --port 8502
   ```

2. **Missing dependencies**
   ```bash
   python startup.py --install-deps
   ```

3. **Azure authentication errors**
   - Verify service principal credentials
   - Check subscription access
   - Ensure Data Factory permissions

4. **AI provider errors**
   - Verify API keys
   - Check rate limits
   - Review provider status

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python startup.py webapp
```

### Log Locations

- Application logs: `logs/adf_monitor.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log`

## 📈 Scaling Considerations

### Horizontal Scaling

1. **Load Balancer Setup**
   - Use Azure Load Balancer or Application Gateway
   - Configure session affinity if needed
   - Implement health checks

2. **Database Scaling**
   - Migrate from SQLite to PostgreSQL/SQL Server
   - Implement connection pooling
   - Consider read replicas

3. **Caching**
   - Implement Redis for session storage
   - Cache configuration data
   - Use CDN for static assets

### Performance Optimization

1. **AI Provider Optimization**
   - Implement request queuing
   - Use connection pooling
   - Cache common analyses

2. **Database Optimization**
   - Index critical queries
   - Implement data retention policies
   - Use database partitioning

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] Service principal permissions verified
- [ ] AI provider API keys tested
- [ ] Notification channels configured
- [ ] SSL/TLS certificates installed
- [ ] Backup procedures established
- [ ] Monitoring alerts configured
- [ ] Security policies implemented
- [ ] Performance testing completed
- [ ] Documentation updated

## 📞 Support

For support and questions:
- Check the troubleshooting section above
- Review application logs
- Consult the configuration guide
- Contact your system administrator

---

**ADF Monitor Pro v2.0** - Enterprise Pipeline Management Platform
*Powered by AI • Built for Scale • Designed for DevOps Teams*
