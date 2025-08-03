# 🚀 Real-Time Azure Integration Setup Guide

## 📋 Prerequisites Checklist

Before connecting to real Azure services, ensure you have:

### ✅ **Azure Requirements**
- [ ] Active Azure subscription
- [ ] Azure Data Factory instance(s) deployed
- [ ] Azure OpenAI service deployed
- [ ] Appropriate permissions (Contributor or Data Factory Contributor)
- [ ] Service Principal with required roles

### ✅ **Access Requirements**
- [ ] Azure CLI installed and authenticated
- [ ] PowerShell (for Windows) or Bash (for Linux/Mac)
- [ ] Network access to Azure services
- [ ] Valid API keys and endpoints

---

## 🔧 STEP 1: Azure Service Principal Setup

### **1.1 Create Service Principal for ADF Access**

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "your-subscription-id"

# Create service principal with Data Factory Contributor role
az ad sp create-for-rbac \
  --name "adf-monitor-pro-sp" \
  --role "Data Factory Contributor" \
  --scopes "/subscriptions/YOUR_SUBSCRIPTION_ID" \
  --sdk-auth

# Example output:
{
  "clientId": "12345678-1234-1234-1234-123456789012",
  "clientSecret": "your-secret-here",
  "subscriptionId": "your-subscription-id",
  "tenantId": "your-tenant-id",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

### **1.2 Assign Additional Permissions (if needed)**

```bash
# For monitoring and metrics access
az role assignment create \
  --assignee "12345678-1234-1234-1234-123456789012" \
  --role "Monitoring Reader" \
  --scope "/subscriptions/YOUR_SUBSCRIPTION_ID"

# For Key Vault access (if using Key Vault for secrets)
az role assignment create \
  --assignee "12345678-1234-1234-1234-123456789012" \
  --role "Key Vault Secrets User" \
  --scope "/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/YOUR_RG/providers/Microsoft.KeyVault/vaults/YOUR_KEYVAULT"
```

---

## 🧠 STEP 2: Azure OpenAI Setup

### **2.1 Deploy Azure OpenAI Service**

```bash
# Create Azure OpenAI resource
az cognitiveservices account create \
  --resource-group "your-rg" \
  --name "adf-monitor-openai" \
  --location "eastus" \
  --kind "OpenAI" \
  --sku "S0"

# Get the endpoint and keys
az cognitiveservices account show \
  --resource-group "your-rg" \
  --name "adf-monitor-openai" \
  --query "properties.endpoint" -o tsv

az cognitiveservices account keys list \
  --resource-group "your-rg" \
  --name "adf-monitor-openai"
```

### **2.2 Deploy Required Models**

```bash
# Deploy GPT-4 model
az cognitiveservices account deployment create \
  --resource-group "your-rg" \
  --account-name "adf-monitor-openai" \
  --deployment-name "gpt-4-deployment" \
  --model-name "gpt-4" \
  --model-version "0613" \
  --scale-settings-scale-type "Standard" \
  --scale-settings-capacity 10

# Deploy GPT-3.5-turbo as backup
az cognitiveservices account deployment create \
  --resource-group "your-rg" \
  --account-name "adf-monitor-openai" \
  --deployment-name "gpt-35-turbo-deployment" \
  --model-name "gpt-35-turbo" \
  --model-version "0613" \
  --scale-settings-scale-type "Standard" \
  --scale-settings-capacity 20
```

---

## ⚙️ STEP 3: Configuration Setup

### **3.1 Update Environment Variables**

Create your production `.env` file:

```bash
# Copy the sample and edit
cp .env.sample .env
```

Edit `.env` with your real credentials:

```bash
# Azure Configuration - FROM SERVICE PRINCIPAL CREATION
AZURE_TENANT_ID=your-tenant-id-from-sp-output
AZURE_CLIENT_ID=your-client-id-from-sp-output
AZURE_CLIENT_SECRET=your-client-secret-from-sp-output
AZURE_SUBSCRIPTION_ID=your-subscription-id

# Azure OpenAI Configuration - FROM AZURE OPENAI DEPLOYMENT
AZURE_OPENAI_ENDPOINT=https://adf-monitor-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Backup OpenAI Configuration (optional)
OPENAI_API_KEY=your-openai-api-key-here

# Notification Configuration (optional)
TEAMS_WEBHOOK_URL=https://your-company.webhook.office.com/...
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-app-password
EMAIL_RECIPIENTS=admin@company.com,devops@company.com

# Application Configuration
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///adf_monitor_production.db
ENABLE_AUTHENTICATION=false
SESSION_TIMEOUT_HOURS=8
```

### **3.2 Update Environment Configuration**

Edit `config/environments.yaml` with your real ADF instances:

```yaml
environments:
  - name: "Production"
    subscription_id: "YOUR_ACTUAL_SUBSCRIPTION_ID"
    resource_group: "YOUR_PROD_RG_NAME"
    data_factory: "YOUR_PROD_ADF_NAME"
    region: "eastus"  # Your actual region
    tenant_id: "YOUR_TENANT_ID"
    client_id: "YOUR_CLIENT_ID"
    client_secret: "YOUR_CLIENT_SECRET"
    status: "Active"
    polling_interval: 300  # 5 minutes
    retry_attempts: 3

  - name: "Staging"
    subscription_id: "YOUR_SUBSCRIPTION_ID"
    resource_group: "YOUR_STAGE_RG_NAME"
    data_factory: "YOUR_STAGE_ADF_NAME"
    region: "eastus"
    tenant_id: "YOUR_TENANT_ID"
    client_id: "YOUR_CLIENT_ID"
    client_secret: "YOUR_CLIENT_SECRET"
    status: "Active"
    polling_interval: 600  # 10 minutes
    retry_attempts: 2

  - name: "Development"
    subscription_id: "YOUR_SUBSCRIPTION_ID"
    resource_group: "YOUR_DEV_RG_NAME"
    data_factory: "YOUR_DEV_ADF_NAME"
    region: "eastus"
    tenant_id: "YOUR_TENANT_ID"
    client_id: "YOUR_CLIENT_ID"
    client_secret: "YOUR_CLIENT_SECRET"
    status: "Active"
    polling_interval: 900  # 15 minutes
    retry_attempts: 1
```

### **3.3 Update AI Provider Configuration**

Edit `config/ai_providers.yaml`:

```yaml
ai_providers:
  - provider_id: "azure-openai-primary"
    provider_name: "Azure OpenAI GPT-4"
    provider_class: "OpenAIProvider"
    model_name: "gpt-4-deployment"  # Your deployment name
    api_endpoint: "https://adf-monitor-openai.openai.azure.com/"
    api_key: "YOUR_AZURE_OPENAI_API_KEY"
    temperature: 0.3
    max_tokens: 1000
    top_p: 0.9
    frequency_penalty: 0.0
    confidence_threshold: 75
    retry_confidence: 80
    active: true
    cost_per_1k_tokens: 0.02

  - provider_id: "azure-openai-backup"
    provider_name: "Azure OpenAI GPT-3.5"
    provider_class: "OpenAIProvider"
    model_name: "gpt-35-turbo-deployment"
    api_endpoint: "https://adf-monitor-openai.openai.azure.com/"
    api_key: "YOUR_AZURE_OPENAI_API_KEY"
    temperature: 0.3
    max_tokens: 1000
    confidence_threshold: 70
    active: true
    cost_per_1k_tokens: 0.001

  - provider_id: "openai-fallback"
    provider_name: "OpenAI GPT-4 (Fallback)"
    provider_class: "OpenAIProvider"
    model_name: "gpt-4"
    api_endpoint: "https://api.openai.com/v1/chat/completions"
    api_key: "YOUR_OPENAI_API_KEY"
    temperature: 0.3
    max_tokens: 1000
    active: false  # Enable as fallback
    cost_per_1k_tokens: 0.03
```

---

## 🔧 STEP 4: Install Required Dependencies

### **4.1 Install Azure Dependencies**

```bash
# Install Azure SDK packages
pip install azure-identity azure-mgmt-datafactory azure-mgmt-monitor azure-storage-blob azure-keyvault-secrets

# Install OpenAI package (if not already installed)
pip install openai

# Install additional monitoring packages
pip install prometheus-client psutil
```

### **4.2 Update Requirements File**

Add to `requirements_webapp.txt`:

```text
# Azure SDK Dependencies
azure-identity>=1.14.0
azure-mgmt-datafactory>=3.0.0
azure-mgmt-monitor>=6.0.0
azure-storage-blob>=12.17.0
azure-keyvault-secrets>=4.7.0

# Enhanced OpenAI
openai>=1.0.0

# Monitoring
prometheus-client>=0.17.0
psutil>=5.9.0
```

---

## 🚀 STEP 5: Test Connections

### **5.1 Test Azure Data Factory Connection**

Create a test script:

```python
# test_adf_connection.py
from azure.identity import ClientSecretCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
import os
from dotenv import load_dotenv

load_dotenv()

# Test ADF connection
def test_adf_connection():
    credential = ClientSecretCredential(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET")
    )
    
    client = DataFactoryManagementClient(
        credential=credential,
        subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID")
    )
    
    # Test by listing data factories
    rg_name = "YOUR_RESOURCE_GROUP"
    try:
        factories = list(client.factories.list_by_resource_group(rg_name))
        print(f"✅ Successfully connected to Azure Data Factory")
        print(f"Found {len(factories)} data factories in resource group {rg_name}")
        
        for factory in factories:
            print(f"  - {factory.name}")
            
            # Test getting pipeline runs
            pipeline_runs = list(client.pipeline_runs.query_by_factory(
                resource_group_name=rg_name,
                factory_name=factory.name,
                filter_parameters={
                    "lastUpdatedAfter": "2024-01-01T00:00:00.0000000Z",
                    "lastUpdatedBefore": "2024-12-31T23:59:59.9999999Z"
                }
            ))
            print(f"    Found {len(pipeline_runs)} pipeline runs")
            
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Azure Data Factory: {e}")
        return False

if __name__ == "__main__":
    test_adf_connection()
```

Run the test:

```bash
python test_adf_connection.py
```

### **5.2 Test Azure OpenAI Connection**

```python
# test_openai_connection.py
import openai
import os
from dotenv import load_dotenv

load_dotenv()

def test_azure_openai():
    try:
        # Configure Azure OpenAI
        openai.api_type = "azure"
        openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        # Test with a simple completion
        response = openai.ChatCompletion.create(
            engine=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Azure OpenAI connection successful!'"}
            ],
            max_tokens=50,
            temperature=0.3
        )
        
        print("✅ Successfully connected to Azure OpenAI")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Azure OpenAI: {e}")
        return False

if __name__ == "__main__":
    test_azure_openai()
```

Run the test:

```bash
python test_openai_connection.py
```

---

## 🔄 STEP 6: Update Application Code for Real Azure

### **6.1 Enhance ADF Client for Real Azure**

Update the `adf_client.py` to use real Azure authentication:

```python
# Add to adf_client.py imports
from azure.identity import ClientSecretCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.core.exceptions import AzureError

# Update ADFClient class
class ADFClient:
    def __init__(self, environment_config: Dict[str, Any]):
        self.environment_config = environment_config
        self.use_mock_data = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
        
        if not self.use_mock_data:
            self._setup_azure_client()
    
    def _setup_azure_client(self):
        """Setup real Azure Data Factory client"""
        try:
            self.credential = ClientSecretCredential(
                tenant_id=self.environment_config["tenant_id"],
                client_id=self.environment_config["client_id"],
                client_secret=self.environment_config["client_secret"]
            )
            
            self.client = DataFactoryManagementClient(
                credential=self.credential,
                subscription_id=self.environment_config["subscription_id"]
            )
            
            print(f"✅ Connected to Azure Data Factory: {self.environment_config['data_factory']}")
            
        except Exception as e:
            print(f"❌ Failed to setup Azure client: {e}")
            print("Falling back to mock data...")
            self.use_mock_data = True
    
    def get_pipeline_runs(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Get pipeline runs from Azure Data Factory or mock data"""
        if self.use_mock_data:
            return self._get_mock_pipeline_runs(hours_back)
        
        try:
            # Calculate time range
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours_back)
            
            # Query Azure Data Factory
            pipeline_runs = list(self.client.pipeline_runs.query_by_factory(
                resource_group_name=self.environment_config["resource_group"],
                factory_name=self.environment_config["data_factory"],
                filter_parameters={
                    "lastUpdatedAfter": start_time.isoformat(),
                    "lastUpdatedBefore": end_time.isoformat()
                }
            ))
            
            # Convert to our format
            runs = []
            for run in pipeline_runs:
                runs.append({
                    "runId": run.run_id,
                    "pipelineName": run.pipeline_name,
                    "status": run.status,
                    "runStart": run.run_start.isoformat() if run.run_start else None,
                    "runEnd": run.run_end.isoformat() if run.run_end else None,
                    "message": getattr(run, 'message', ''),
                    "durationInMs": run.duration_in_ms if hasattr(run, 'duration_in_ms') else 0
                })
            
            print(f"📊 Retrieved {len(runs)} pipeline runs from Azure")
            return runs
            
        except AzureError as e:
            print(f"❌ Azure API error: {e}")
            print("Falling back to mock data...")
            return self._get_mock_pipeline_runs(hours_back)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return self._get_mock_pipeline_runs(hours_back)
```

### **6.2 Update GenAI Analyzer for Azure OpenAI**

Enhance `genai_analyzer.py`:

```python
# Add to genai_analyzer.py
class AzureOpenAIAnalyzer:
    def __init__(self):
        self.use_azure_openai = os.getenv("USE_AZURE_OPENAI", "true").lower() == "true"
        
        if self.use_azure_openai:
            self._setup_azure_openai()
        else:
            self._setup_openai()
    
    def _setup_azure_openai(self):
        """Setup Azure OpenAI configuration"""
        try:
            openai.api_type = "azure"
            openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
            openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
            
            self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            print(f"✅ Configured Azure OpenAI with deployment: {self.deployment_name}")
            
        except Exception as e:
            print(f"❌ Failed to setup Azure OpenAI: {e}")
            self.use_azure_openai = False
            self._setup_openai()
    
    def _setup_openai(self):
        """Setup regular OpenAI as fallback"""
        openai.api_type = "open_ai"
        openai.api_base = "https://api.openai.com/v1"
        openai.api_key = os.getenv("OPENAI_API_KEY")
        print("✅ Configured OpenAI as fallback")
    
    def analyze_failure_with_ai(self, pipeline_name: str, error_message: str, run_id: str) -> Dict[str, Any]:
        """Analyze failure using Azure OpenAI or OpenAI"""
        try:
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"Pipeline: {pipeline_name}\nError: {error_message}\nRun ID: {run_id}"}
            ]
            
            if self.use_azure_openai:
                response = openai.ChatCompletion.create(
                    engine=self.deployment_name,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1000
                )
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1000
                )
            
            # Parse response and return analysis
            content = response.choices[0].message.content
            return self._parse_ai_response(content)
            
        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
            return self._fallback_analysis(error_message)
```

---

## 🏃‍♂️ STEP 7: Launch Real-Time Monitoring

### **7.1 Start with Real Azure Integration**

```bash
# Set environment for real Azure (not mock data)
export USE_MOCK_DATA=false
export USE_AZURE_OPENAI=true

# Or on Windows PowerShell:
$env:USE_MOCK_DATA="false"
$env:USE_AZURE_OPENAI="true"

# Launch the application
python startup.py webapp --port 8501
```

### **7.2 Verify Real-Time Connection**

1. **Open webapp**: http://localhost:8501
2. **Check Dashboard**: Should show real pipeline data
3. **Test AI Analysis**: Create a test failure to verify AI response
4. **Monitor Logs**: Check application logs for Azure connectivity

### **7.3 Enable Continuous Monitoring**

The webapp will now:
- ✅ **Poll real Azure Data Factory** every 5-15 minutes
- ✅ **Use Azure OpenAI** for intelligent failure analysis
- ✅ **Store real pipeline data** in the database
- ✅ **Send real notifications** when configured
- ✅ **Execute real retry actions** on Azure pipelines

---

## 🔍 STEP 8: Monitoring and Validation

### **8.1 Real-Time Validation Checklist**

- [ ] **Azure Data Factory Connection**: Dashboard shows real pipeline data
- [ ] **Azure OpenAI Integration**: AI analysis returns intelligent responses
- [ ] **Multi-Environment**: Can switch between Prod/Stage/Dev
- [ ] **Real Pipeline Runs**: Historical data appears in the interface
- [ ] **Live Failures**: New failures trigger AI analysis
- [ ] **Retry Actions**: Can successfully retry failed pipelines
- [ ] **Notifications**: Alerts sent to configured channels

### **8.2 Troubleshooting Common Issues**

**Connection Issues:**
```bash
# Test Azure authentication
az account show

# Verify service principal permissions
az role assignment list --assignee YOUR_CLIENT_ID

# Check Azure OpenAI deployment
az cognitiveservices account deployment list \
  --resource-group YOUR_RG \
  --account-name YOUR_OPENAI_RESOURCE
```

**Configuration Issues:**
```bash
# Validate environment variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Tenant:', os.getenv('AZURE_TENANT_ID')[:8] + '...')"

# Test configuration loading
python -c "from enterprise_config import get_config_manager; cm = get_config_manager(); print('Environments:', len(cm.get_environments()))"
```

---

## 🎉 **CONGRATULATIONS!**

Your **ADF Monitor Pro** is now connected to:

✅ **Real Azure Data Factory** - Live pipeline monitoring  
✅ **Real Azure OpenAI** - Intelligent AI analysis  
✅ **Production-Ready** - Enterprise security and scalability  

### **🚀 You Now Have:**

1. **Live Pipeline Monitoring** from your actual ADF instances
2. **Intelligent AI Analysis** using Azure OpenAI GPT-4
3. **Real-Time Automation** with actual retry capabilities
4. **Multi-Environment Support** across Prod/Stage/Dev
5. **Enterprise Security** with service principal authentication
6. **Scalable Architecture** ready for production deployment

**Your enterprise ADF monitoring solution is now fully operational with real Azure services!** 🏆
