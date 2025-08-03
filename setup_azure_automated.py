"""
Azure Setup Automation Script
Automates the Azure service principal and resource setup process
"""
import os
import sys
import subprocess
import json
import time
from datetime import datetime

def run_azure_cli_command(command, description=""):
    """Run Azure CLI command and return result"""
    print(f"🔧 {description or 'Running Azure command'}...")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        if result.stdout.strip():
            try:
                # Try to parse as JSON for structured output
                json_result = json.loads(result.stdout)
                return {"success": True, "data": json_result, "raw": result.stdout}
            except json.JSONDecodeError:
                # Return as text if not JSON
                return {"success": True, "data": result.stdout.strip(), "raw": result.stdout}
        else:
            return {"success": True, "data": None, "raw": result.stdout}
            
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Command failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return {"success": False, "error": str(e), "stderr": e.stderr}

def check_azure_cli():
    """Check if Azure CLI is installed and user is logged in"""
    print("🔍 Checking Azure CLI...")
    
    # Check if Azure CLI is installed
    result = run_azure_cli_command("az --version", "Checking Azure CLI installation")
    if not result["success"]:
        print("❌ Azure CLI is not installed")
        print("💡 Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    
    print("✅ Azure CLI is installed")
    
    # Check if logged in
    result = run_azure_cli_command("az account show", "Checking Azure CLI login status")
    if not result["success"]:
        print("❌ Not logged into Azure CLI")
        print("💡 Run: az login")
        return False
    
    account_info = result["data"]
    print(f"✅ Logged in as: {account_info.get('user', {}).get('name', 'Unknown')}")
    print(f"✅ Subscription: {account_info.get('name', 'Unknown')} ({account_info.get('id', 'Unknown')})")
    
    return True

def get_or_create_resource_group():
    """Get or create resource group for ADF monitoring"""
    print("\n📁 Setting up Resource Group...")
    
    rg_name = "rg-adf-monitoring"
    location = "East US"
    
    # Check if resource group exists
    result = run_azure_cli_command(
        f"az group show --name {rg_name}",
        f"Checking if resource group '{rg_name}' exists"
    )
    
    if result["success"]:
        print(f"✅ Resource group '{rg_name}' already exists")
        return rg_name
    else:
        # Create resource group
        print(f"🆕 Creating resource group '{rg_name}'...")
        result = run_azure_cli_command(
            f"az group create --name {rg_name} --location \"{location}\"",
            f"Creating resource group in {location}"
        )
        
        if result["success"]:
            print(f"✅ Resource group '{rg_name}' created successfully")
            return rg_name
        else:
            print(f"❌ Failed to create resource group: {result.get('error', 'Unknown error')}")
            return None

def create_service_principal():
    """Create service principal for ADF monitoring"""
    print("\n👤 Creating Service Principal...")
    
    sp_name = "sp-adf-monitoring"
    
    # Create service principal with Data Factory Contributor role
    result = run_azure_cli_command(
        f"az ad sp create-for-rbac --name {sp_name} --role \"Data Factory Contributor\" --scope /subscriptions/$(az account show --query id -o tsv)",
        "Creating service principal with Data Factory Contributor role"
    )
    
    if result["success"]:
        sp_info = result["data"]
        print("✅ Service principal created successfully")
        print(f"   App ID: {sp_info.get('appId', 'Unknown')}")
        print(f"   Tenant: {sp_info.get('tenant', 'Unknown')}")
        print("   🔐 Secret: [Hidden for security]")
        
        return {
            "client_id": sp_info.get("appId"),
            "client_secret": sp_info.get("password"),
            "tenant_id": sp_info.get("tenant")
        }
    else:
        print(f"❌ Failed to create service principal: {result.get('error', 'Unknown error')}")
        return None

def deploy_azure_openai():
    """Deploy Azure OpenAI service"""
    print("\n🧠 Deploying Azure OpenAI...")
    
    openai_name = f"openai-adf-monitoring-{int(time.time())}"  # Unique name
    rg_name = "rg-adf-monitoring"
    location = "East US"
    
    # Create Azure OpenAI resource
    result = run_azure_cli_command(
        f"az cognitiveservices account create --name {openai_name} --resource-group {rg_name} --kind OpenAI --sku S0 --location \"{location}\" --yes",
        "Creating Azure OpenAI resource"
    )
    
    if not result["success"]:
        print(f"❌ Failed to create Azure OpenAI resource: {result.get('error', 'Unknown error')}")
        return None
    
    print("✅ Azure OpenAI resource created")
    
    # Get the keys
    result = run_azure_cli_command(
        f"az cognitiveservices account keys list --name {openai_name} --resource-group {rg_name}",
        "Retrieving Azure OpenAI keys"
    )
    
    if not result["success"]:
        print("❌ Failed to retrieve Azure OpenAI keys")
        return None
    
    keys = result["data"]
    
    # Create model deployment
    deployment_name = "gpt-4-deployment"
    print(f"🚀 Creating model deployment '{deployment_name}'...")
    
    result = run_azure_cli_command(
        f"az cognitiveservices account deployment create --name {openai_name} --resource-group {rg_name} --deployment-name {deployment_name} --model-name gpt-4 --model-version \"0613\" --model-format OpenAI --sku-capacity 10 --sku-name Standard",
        "Creating GPT-4 deployment"
    )
    
    if result["success"]:
        print("✅ GPT-4 deployment created successfully")
    else:
        print("⚠️ GPT-4 deployment failed, trying GPT-3.5 Turbo...")
        deployment_name = "gpt-35-turbo-deployment"
        
        result = run_azure_cli_command(
            f"az cognitiveservices account deployment create --name {openai_name} --resource-group {rg_name} --deployment-name {deployment_name} --model-name gpt-35-turbo --model-version \"0613\" --model-format OpenAI --sku-capacity 10 --sku-name Standard",
            "Creating GPT-3.5 Turbo deployment"
        )
        
        if result["success"]:
            print("✅ GPT-3.5 Turbo deployment created successfully")
        else:
            print("❌ Failed to create model deployment")
    
    return {
        "resource_name": openai_name,
        "endpoint": f"https://{openai_name}.openai.azure.com/",
        "api_key": keys.get("key1"),
        "deployment_name": deployment_name
    }

def find_data_factories():
    """Find existing Data Factories in the subscription"""
    print("\n🏭 Searching for Azure Data Factories...")
    
    result = run_azure_cli_command(
        "az datafactory list --query \"[].{name:name, resourceGroup:resourceGroup, location:location}\" -o table",
        "Listing Azure Data Factories"
    )
    
    if result["success"] and result["data"]:
        print("✅ Found Data Factories:")
        print(result["data"])
        return True
    else:
        print("⚠️ No Data Factories found in current subscription")
        print("💡 Create one at: https://portal.azure.com/#create/Microsoft.DataFactory")
        return False

def generate_environment_file(sp_info, openai_info):
    """Generate .env file with all configuration"""
    print("\n📝 Generating environment configuration...")
    
    env_content = f"""# Azure Service Principal Configuration
AZURE_CLIENT_ID={sp_info['client_id']}
AZURE_CLIENT_SECRET={sp_info['client_secret']}
AZURE_TENANT_ID={sp_info['tenant_id']}
AZURE_SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT={openai_info['endpoint']}
AZURE_OPENAI_API_KEY={openai_info['api_key']}
AZURE_OPENAI_DEPLOYMENT_NAME={openai_info['deployment_name']}
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Application Configuration
USE_AZURE_OPENAI=true
ADF_MONITORING_ENABLED=true
LOG_LEVEL=INFO

# Web Application
STREAMLIT_HOST=0.0.0.0
STREAMLIT_PORT=8502

# Generated on: {datetime.now().isoformat()}
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Environment file created: .env")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def update_config_files(openai_info):
    """Update YAML configuration files"""
    print("\n⚙️ Updating configuration files...")
    
    # Update environments.yaml
    env_config = f"""environments:
  production:
    name: "Production"
    description: "Live Azure Data Factory monitoring"
    azure_tenant_id: "${{AZURE_TENANT_ID}}"
    azure_subscription_id: "${{AZURE_SUBSCRIPTION_ID}}"
    azure_client_id: "${{AZURE_CLIENT_ID}}"
    azure_client_secret: "${{AZURE_CLIENT_SECRET}}"
    monitoring_enabled: true
    log_level: "INFO"
    refresh_interval: 300
    ai_analysis_enabled: true
    
  staging:
    name: "Staging"
    description: "Pre-production testing"
    azure_tenant_id: "${{AZURE_TENANT_ID}}"
    azure_subscription_id: "${{AZURE_SUBSCRIPTION_ID}}"
    azure_client_id: "${{AZURE_CLIENT_ID}}"
    azure_client_secret: "${{AZURE_CLIENT_SECRET}}"
    monitoring_enabled: true
    log_level: "DEBUG"
    refresh_interval: 60
    ai_analysis_enabled: true
    
  development:
    name: "Development"
    description: "Local development and testing"
    monitoring_enabled: false
    log_level: "DEBUG"
    refresh_interval: 30
    ai_analysis_enabled: true
"""
    
    # Update ai_providers.yaml
    ai_config = f"""ai_providers:
  - provider_id: "azure-openai-production"
    provider_name: "Azure OpenAI (Production)"
    provider_class: "OpenAIProvider"
    model_name: "{openai_info['deployment_name']}"
    api_endpoint: "{openai_info['endpoint']}"
    api_key: "${{AZURE_OPENAI_API_KEY}}"
    api_version: "2024-02-15-preview"
    temperature: 0.3
    max_tokens: 1000
    top_p: 0.9
    frequency_penalty: 0.0
    confidence_threshold: 75
    retry_confidence: 80
    active: true
    cost_per_1k_tokens: 0.02
    
  - provider_id: "azure-openai-backup"
    provider_name: "Azure OpenAI (Backup)"
    provider_class: "OpenAIProvider"
    model_name: "gpt-35-turbo-deployment"
    api_endpoint: "{openai_info['endpoint']}"
    api_key: "${{AZURE_OPENAI_API_KEY}}"
    api_version: "2024-02-15-preview"
    temperature: 0.3
    max_tokens: 800
    confidence_threshold: 70
    active: false
    cost_per_1k_tokens: 0.001
"""
    
    try:
        os.makedirs("config", exist_ok=True)
        
        with open("config/environments.yaml", "w") as f:
            f.write(env_config)
        print("✅ Updated config/environments.yaml")
        
        with open("config/ai_providers.yaml", "w") as f:
            f.write(ai_config)
        print("✅ Updated config/ai_providers.yaml")
        
        return True
    except Exception as e:
        print(f"❌ Failed to update config files: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Azure ADF Monitoring Setup Automation")
    print("=" * 60)
    print("This script will:")
    print("1. Check Azure CLI setup")
    print("2. Create/verify resource group")
    print("3. Create service principal for ADF access")
    print("4. Deploy Azure OpenAI service")
    print("5. Create model deployments")
    print("6. Generate configuration files")
    print("7. Validate connections")
    print("=" * 60)
    
    # Ask for confirmation
    confirm = input("\n🤔 Do you want to proceed with the setup? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Setup cancelled by user")
        return
    
    # Step 1: Check Azure CLI
    if not check_azure_cli():
        print("\n❌ Azure CLI setup required. Please fix and run again.")
        return
    
    # Step 2: Setup resource group
    rg_name = get_or_create_resource_group()
    if not rg_name:
        print("\n❌ Resource group setup failed")
        return
    
    # Step 3: Create service principal
    sp_info = create_service_principal()
    if not sp_info:
        print("\n❌ Service principal creation failed")
        return
    
    # Step 4: Deploy Azure OpenAI
    openai_info = deploy_azure_openai()
    if not openai_info:
        print("\n❌ Azure OpenAI deployment failed")
        return
    
    # Step 5: Find Data Factories
    find_data_factories()
    
    # Step 6: Generate configuration
    if not generate_environment_file(sp_info, openai_info):
        print("\n❌ Configuration generation failed")
        return
    
    if not update_config_files(openai_info):
        print("\n❌ Config file updates failed")
        return
    
    # Success summary
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("✅ Service Principal created")
    print("✅ Azure OpenAI deployed")
    print("✅ Configuration files generated")
    print("✅ Environment variables set")
    
    print("\n📋 NEXT STEPS:")
    print("1. Run: python test_adf_connection.py")
    print("2. Run: python test_openai_connection.py")
    print("3. Run: python startup.py webapp")
    print("4. Open: http://localhost:8502")
    
    print("\n🔐 SECURITY NOTES:")
    print("- Your service principal credentials are in .env")
    print("- Keep these credentials secure and never commit to git")
    print("- Consider using Azure Key Vault for production")
    
    print("\n💰 COST CONSIDERATIONS:")
    print("- Azure OpenAI has usage-based pricing")
    print("- Monitor usage in Azure portal")
    print("- Set up billing alerts if needed")

if __name__ == "__main__":
    main()
