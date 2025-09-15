# ADF Monitor Pro - Configuration Summary

## Quick Start Commands

### 1. One-Click Deployment (Recommended for beginners)
```powershell
# Navigate to the scripts folder
cd "d:\Knowledge_Hub\AIMS\azure-deployment\scripts"

# Run quick start deployment
.\QuickStart-Deploy.ps1
```

### 2. Custom Deployment
```powershell
# Full deployment with custom parameters
.\Deploy-ADF-Monitor-Test-Environment.ps1 `
    -SubscriptionId "your-subscription-id" `
    -ResourceGroupName "adf-monitor-test-rg" `
    -Location "East US" `
    -Environment "dev" `
    -AdminEmail "your.email@company.com" `
    -DeployWebApp $true `
    -CreateTestData $true
```

### 3. Validate Deployment
```powershell
# Validate all resources are working
.\Validate-Deployment.ps1 `
    -ResourceGroupName "adf-monitor-test-rg" `
    -SubscriptionId "your-subscription-id"
```

### 4. Clean Up Resources
```powershell
# Complete cleanup (removes everything)
.\Cleanup-Deployment.ps1 `
    -ResourceGroupName "adf-monitor-test-rg" `
    -SubscriptionId "your-subscription-id"

# What-if analysis (shows what would be deleted)
.\Cleanup-Deployment.ps1 `
    -ResourceGroupName "adf-monitor-test-rg" `
    -SubscriptionId "your-subscription-id" `
    -WhatIf
```

## Environment-Specific Deployments

### Development Environment
```powershell
.\Deploy-ADF-Monitor-Test-Environment.ps1 `
    -SubscriptionId "your-subscription-id" `
    -ResourceGroupName "adf-monitor-dev-rg" `
    -Environment "dev" `
    -AdminEmail "dev@company.com"
```

### Staging Environment  
```powershell
.\Deploy-ADF-Monitor-Test-Environment.ps1 `
    -SubscriptionId "your-subscription-id" `
    -ResourceGroupName "adf-monitor-staging-rg" `
    -Environment "staging" `
    -AdminEmail "staging@company.com"
```

### Production Environment
```powershell
.\Deploy-ADF-Monitor-Test-Environment.ps1 `
    -SubscriptionId "your-subscription-id" `
    -ResourceGroupName "adf-monitor-prod-rg" `
    -Environment "prod" `
    -AdminEmail "admin@company.com"
```

## Running the Application

After deployment, configure your application to connect to the deployed resources:

1. **Update Configuration**: Modify `webapp.py` with the deployed resource names (provided in deployment output)

2. **Run the Application**:
   ```powershell
   # Navigate to the main application folder
   cd "d:\Knowledge_Hub\AIMS"
   
   # Install dependencies (if not already done)
   pip install -r requirements.txt
   
   # Run the monitoring application
   streamlit run webapp.py
   ```

3. **Access the Application**: Open your browser to `http://localhost:8501`

## File Structure Overview

```
azure-deployment/
├── scripts/
│   ├── Deploy-ADF-Monitor-Test-Environment.ps1  # Main deployment script
│   ├── QuickStart-Deploy.ps1                    # Simplified deployment
│   ├── Validate-Deployment.ps1                  # Validation script
│   └── Cleanup-Deployment.ps1                   # Resource cleanup
├── infrastructure/
│   ├── main.bicep                               # Main infrastructure template
│   ├── main.parameters.dev.json                # Development parameters
│   ├── main.parameters.staging.json            # Staging parameters
│   └── main.parameters.prod.json               # Production parameters
├── adf-templates/
│   ├── DataIngestionPipeline.json              # Sample data ingestion pipeline
│   ├── ETLTransformPipeline.json               # Sample ETL pipeline
│   ├── ReportGenerationPipeline.json           # Sample reporting pipeline
│   └── DataValidationPipeline.json             # Sample validation pipeline
├── test-data/
│   ├── customer_data_good.csv                  # Clean test data
│   ├── customer_data_with_errors.csv           # Data with errors
│   ├── customer_data_wrong_format.csv          # Incorrectly formatted data
│   ├── database-setup.sql                     # Database schema and data
│   └── test-scenarios.md                      # Detailed test scenarios
└── README.md                                   # Comprehensive documentation
```

## Troubleshooting Quick Reference

### Common Issues and Solutions

1. **Authentication Error**
   ```powershell
   # Solution: Login to Azure
   az login
   az account set --subscription "your-subscription-id"
   ```

2. **Permission Denied**
   ```
   Error: The client does not have authorization to perform action
   ```
   - Ensure your account has Contributor role on the subscription
   - Contact your Azure administrator

3. **Resource Name Already Exists**
   ```
   Error: Storage account name is already taken
   ```
   - Use a different resource group name
   - Add `-Force $true` parameter to use existing resources

4. **Network Connectivity Issues**
   - Check corporate firewall settings
   - Configure proxy settings if needed
   - Try different Azure regions

### Getting Help

- **View detailed logs**: Add `-Verbose` parameter to any script
- **Check Azure Portal**: Monitor deployment progress at portal.azure.com
- **Validate resources**: Use the validation script after deployment
- **Cost monitoring**: Check Azure Cost Management for spending

## Default Resource Names

The deployment creates resources with predictable naming patterns:

- **Storage Account**: `adfmon{env}{unique-suffix}`
- **Data Factory**: `adfmon-{env}-adf-{unique-suffix}`
- **SQL Server**: `adfmon-{env}-sql-{unique-suffix}`
- **Key Vault**: `adfmon-{env}-kv-{unique-suffix}`
- **Log Analytics**: `adfmon-{env}-logs-{unique-suffix}`
- **App Service**: `adfmon-{env}-app-{unique-suffix}`

Where `{env}` is your environment (dev/staging/prod) and `{unique-suffix}` is automatically generated.

## Security Notes

⚠️ **Important**: This deployment uses default passwords and settings suitable for testing only.

**For production use, please:**
- Change all default passwords
- Configure Azure AD authentication
- Enable firewall rules
- Set up private endpoints
- Configure managed identities
- Enable Advanced Threat Protection

## Cost Estimation

Approximate monthly costs (USD):

- **Development**: $50-100
- **Staging**: $100-200  
- **Production**: $200-500+

Costs vary based on usage, region, and SKU selections.

---

Ready to deploy? Start with the **QuickStart-Deploy.ps1** script for the easiest experience!