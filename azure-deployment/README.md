# ADF Monitor Pro - One-Click Azure Deployment Guide

## Overview

This deployment package creates a complete Azure test environment for ADF Monitor Pro with all necessary resources, test data, and failure scenarios. Perfect for corporate laptops where you only have Azure subscription access.

## What Gets Deployed

### Azure Resources
- **Azure Data Factory** - With sample pipelines and monitoring
- **Storage Account** - With Data Lake Gen2 for test data
- **SQL Database** - With sample schema and test data
- **Key Vault** - For secure secret management
- **Log Analytics** - For comprehensive monitoring
- **App Service** - For the monitoring web application
- **Application Insights** - For application performance monitoring

### Sample Data & Scenarios
- Customer data files (good, error, wrong format)
- Realistic ADF pipelines with success/failure scenarios
- SQL database with tables, stored procedures, and sample data
- Pre-configured monitoring queries and dashboards

## Prerequisites

### Required
1. **Azure Subscription** - With Contributor permissions
2. **PowerShell 7.0+** - For running the deployment script
3. **Azure CLI** or **Azure PowerShell** - For Azure authentication

### Optional (for enhanced features)
- **SQL Server Management Studio** or **Azure Data Studio** - For database management
- **Visual Studio Code** - For code editing and development

### Corporate Network Considerations
- Ensure firewall allows connections to *.windows.net
- Proxy settings may need configuration for Azure CLI/PowerShell
- Some corporate networks block certain Azure regions

## Installation Steps

### Step 1: Install Prerequisites

#### Option A: Install Azure CLI (Recommended for corporate environments)
```powershell
# Download and install Azure CLI from: https://aka.ms/installazurecliwindows
# Or use winget (if available)
winget install -e --id Microsoft.AzureCLI
```

#### Option B: Install Azure PowerShell
```powershell
# Install Azure PowerShell modules (requires admin rights)
Install-Module -Name Az -Repository PSGallery -Force -AllowClobber
```

### Step 2: Download and Prepare

1. **Extract the deployment package** to a local folder (e.g., `C:\ADF-Monitor-Deployment`)
2. **Open PowerShell** and navigate to the scripts folder:
   ```powershell
   cd "C:\ADF-Monitor-Deployment\azure-deployment\scripts"
   ```

### Step 3: Run Deployment

#### Quick Start (Development Environment)
```powershell
.\Deploy-ADF-Monitor-Test-Environment.ps1 -SubscriptionId "your-subscription-id" -ResourceGroupName "adf-monitor-dev-rg" -AdminEmail "your.email@company.com"
```

#### Full Deployment with Options
```powershell
.\Deploy-ADF-Monitor-Test-Environment.ps1 `
    -SubscriptionId "12345678-1234-1234-1234-123456789012" `
    -ResourceGroupName "adf-monitor-test-rg" `
    -Location "East US" `
    -Environment "dev" `
    -AdminEmail "admin@company.com" `
    -DeployWebApp $true `
    -CreateTestData $true `
    -Force $false
```

#### Production Deployment
```powershell
.\Deploy-ADF-Monitor-Test-Environment.ps1 `
    -SubscriptionId "your-subscription-id" `
    -ResourceGroupName "adf-monitor-prod-rg" `
    -Location "East US" `
    -Environment "prod" `
    -AdminEmail "admin@company.com"
```

### Step 4: Verify Deployment

The script will provide a deployment summary with all resource details. Verify:

1. **Azure Portal** - Check all resources are created
2. **Storage Account** - Verify test data is uploaded
3. **Data Factory** - Check pipelines are deployed
4. **SQL Database** - Verify schema and sample data
5. **Log Analytics** - Check monitoring data is flowing

## Deployment Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `SubscriptionId` | Yes | - | Your Azure subscription ID |
| `ResourceGroupName` | Yes | - | Name for the resource group |
| `Location` | No | "East US" | Azure region for deployment |
| `Environment` | No | "dev" | Environment type (dev/staging/prod) |
| `AdminEmail` | Yes | - | Email for notifications and alerts |
| `DeployWebApp` | No | true | Whether to deploy the monitoring web app |
| `CreateTestData` | No | true | Whether to create test data and failures |
| `Force` | No | false | Skip confirmation prompts |

## Environment-Specific Configurations

### Development (dev)
- **SKU**: Basic/B1 (cost-optimized)
- **Storage**: Locally redundant (LRS)
- **Purpose**: Testing and development

### Staging (staging)
- **SKU**: Standard/S1 (moderate performance)
- **Storage**: Geo-redundant (GRS)
- **Purpose**: Pre-production testing

### Production (prod)
- **SKU**: Premium/P1V2 (high performance)
- **Storage**: Geo-redundant (GRS)
- **Purpose**: Live production workloads

## Troubleshooting

### Common Issues

#### Authentication Issues
```
Error: Please run 'az login' to setup account
```
**Solution**: Run `az login` and follow the authentication prompts.

#### Permission Issues
```
Error: The client does not have authorization to perform action
```
**Solution**: Ensure your account has Contributor permissions on the subscription.

#### Resource Name Conflicts
```
Error: Storage account name is already taken
```
**Solution**: Use a different resource group name or add the `-Force $true` parameter.

#### Network Connectivity Issues
```
Error: Unable to connect to Azure endpoints
```
**Solution**: Check corporate firewall settings and proxy configuration.

### Corporate Environment Fixes

#### Proxy Configuration
```powershell
# Configure Azure CLI for proxy
az config set core.proxy_host="your-proxy-host"
az config set core.proxy_port="your-proxy-port"

# Configure PowerShell for proxy
$proxy = New-Object System.Net.WebProxy("http://your-proxy:port")
[System.Net.WebRequest]::DefaultWebProxy = $proxy
```

#### Alternative Regions
If East US is blocked, try other regions:
```powershell
-Location "West US 2"  # or
-Location "Central US"  # or
-Location "West Europe"
```

### Getting Help

#### View Full Error Details
```powershell
$ErrorActionPreference = "Continue"
.\Deploy-ADF-Monitor-Test-Environment.ps1 -Verbose
```

#### Check Azure Resource Status
```powershell
# List all resources in the group
az resource list --resource-group "your-rg-name" --output table

# Check specific resource
az resource show --resource-group "your-rg-name" --name "your-resource-name" --resource-type "Microsoft.DataFactory/factories"
```

## Post-Deployment Configuration

### 1. Update Configuration Files

After deployment, update the monitoring application configuration:

```python
# In webapp.py or config file
AZURE_CONFIG = {
    'subscription_id': 'your-subscription-id',
    'resource_group': 'your-resource-group-name',
    'data_factory_name': 'your-adf-name',  # From deployment output
    'storage_account': 'your-storage-name'  # From deployment output
}
```

### 2. Set Up Monitoring

1. **Configure Log Analytics queries** for your specific monitoring needs
2. **Set up alerts** in Azure Monitor for critical failures
3. **Configure email notifications** for pipeline failures
4. **Create custom dashboards** in Azure Portal

### 3. Load Test Data

Run the monitoring application and verify:
- Data Factory pipelines are visible
- Pipeline runs show both successes and failures
- Multi-environment view works (if using multiple deployments)
- Light/Dark theme switching works
- Export functionality works

### 4. Security Hardening (For Production)

⚠️ **Important**: This deployment uses default passwords suitable only for testing.

**For production use:**
1. **Change all default passwords** in Key Vault
2. **Configure Azure AD authentication** for SQL Database
3. **Enable firewall rules** for Storage Account and SQL Database
4. **Set up private endpoints** for enhanced security
5. **Configure managed identities** instead of connection strings
6. **Enable Advanced Threat Protection** for SQL Database
7. **Set up backup and disaster recovery**

## Testing the Environment

### Verify Base Functionality
1. Navigate to Azure Data Factory in the portal
2. Check that sample pipelines are deployed
3. Trigger a few pipeline runs manually
4. Verify data appears in Storage Account containers

### Test the Monitoring Application
1. Run the monitoring webapp locally or access the deployed App Service
2. Select different environments (if deployed multiple)
3. View pipeline failures and successes
4. Test the multi-environment failure view
5. Switch between light and dark themes
6. Export data to verify functionality

### Advanced Testing
Review the `test-scenarios.md` file for detailed test scenarios including:
- Data quality failures
- Connection failures  
- Timeout scenarios
- Resource limit scenarios
- Performance degradation scenarios

## Cleanup

### Remove All Resources
```powershell
# Delete the entire resource group (WARNING: This removes everything!)
az group delete --name "your-resource-group-name" --yes --no-wait
```

### Selective Cleanup
```powershell
# Delete specific resources only
az resource delete --resource-group "your-rg" --name "resource-name" --resource-type "resource-type"
```

## Cost Management

### Estimated Monthly Costs (USD)

| Environment | Basic | Standard | Premium |
|-------------|--------|----------|---------|
| Development | $50-100 | $100-200 | $200-400 |
| Staging | $100-200 | $200-400 | $400-800 |
| Production | $200-500 | $500-1000 | $1000-2000 |

*Costs vary based on usage, region, and data transfer*

### Cost Optimization Tips
1. **Use Development SKUs** for testing
2. **Stop resources** when not in use
3. **Monitor usage** with Azure Cost Management
4. **Set up budget alerts** to avoid surprises
5. **Use reserved instances** for production workloads

## Support & Additional Resources

### Documentation
- [Azure Data Factory Documentation](https://docs.microsoft.com/en-us/azure/data-factory/)
- [Azure Monitor Documentation](https://docs.microsoft.com/en-us/azure/azure-monitor/)
- [Azure SQL Database Documentation](https://docs.microsoft.com/en-us/azure/azure-sql/)

### Community Resources
- [Azure Data Factory Community](https://techcommunity.microsoft.com/t5/azure-data-factory/bd-p/AzureDataFactory)
- [Stack Overflow - Azure Data Factory](https://stackoverflow.com/questions/tagged/azure-data-factory)

### Enterprise Support
For enterprise environments, consider:
- **Azure Support Plans** for direct Microsoft support
- **Professional Services** for complex deployments
- **Partner Solutions** for specialized requirements

---

*This deployment package is designed for testing and development. Please review and adjust security settings for production use.*