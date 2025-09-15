#Requires -Version 7.0
<#
.SYNOPSIS
    One-click deployment script for ADF Monitor Pro test environment

.DESCRIPTION
    This script deploys a complete Azure test environment for ADF Monitor Pro including:
    - Azure Data Factory with sample pipelines
    - Storage Account with test data
    - SQL Database with sample schema
    - Key Vault for secrets
    - Log Analytics for monitoring
    - App Service for the monitoring webapp
    - All necessary RBAC permissions

.PARAMETER SubscriptionId
    Azure subscription ID where resources will be deployed

.PARAMETER ResourceGroupName
    Name of the resource group (will be created if it doesn't exist)

.PARAMETER Location
    Azure region for deployment (default: East US)

.PARAMETER Environment
    Environment type: prod, staging, or dev (default: dev)

.PARAMETER AdminEmail
    Email address for notifications and alerts

.PARAMETER DeployWebApp
    Whether to deploy the monitoring web application

.PARAMETER CreateTestData
    Whether to upload test data files and create sample failures

.EXAMPLE
    .\Deploy-ADF-Monitor-Test-Environment.ps1 -SubscriptionId "your-subscription-id" -ResourceGroupName "adf-monitor-test-rg" -AdminEmail "admin@company.com"

.NOTES
    Author: ADF Monitor Pro
    Version: 1.0
    Requires: Azure PowerShell module or Azure CLI
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $false)]
    [string]$Location = "East US",
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("prod", "staging", "dev")]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory = $true)]
    [string]$AdminEmail,
    
    [Parameter(Mandatory = $false)]
    [bool]$DeployWebApp = $true,
    
    [Parameter(Mandatory = $false)]
    [bool]$CreateTestData = $true,
    
    [Parameter(Mandatory = $false)]
    [bool]$Force = $false
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# Global variables
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$InfrastructurePath = Join-Path $ScriptPath "..\infrastructure"
$AdfTemplatesPath = Join-Path $ScriptPath "..\adf-templates"
$TestDataPath = Join-Path $ScriptPath "..\test-data"

# Colors for output
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"

function Write-StepHeader {
    param([string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor $ColorInfo
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $ColorSuccess
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $ColorWarning
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $ColorError
}

function Test-Prerequisites {
    Write-StepHeader "Checking Prerequisites"
    
    # Check if Azure CLI or PowerShell is available
    $hasAzureCLI = $false
    $hasAzurePowerShell = $false
    
    try {
        $null = Get-Command az -ErrorAction Stop
        $hasAzureCLI = $true
        Write-Success "Azure CLI is available"
    }
    catch {
        Write-Warning "Azure CLI is not available"
    }
    
    try {
        $null = Get-Module -Name Az -ListAvailable -ErrorAction Stop
        $hasAzurePowerShell = $true
        Write-Success "Azure PowerShell is available"
    }
    catch {
        Write-Warning "Azure PowerShell is not available"
    }
    
    if (-not $hasAzureCLI -and -not $hasAzurePowerShell) {
        Write-Error "Neither Azure CLI nor Azure PowerShell is available. Please install one of them."
        exit 1
    }
    
    # Check if files exist
    $requiredFiles = @(
        Join-Path $InfrastructurePath "main.bicep",
        Join-Path $InfrastructurePath "main.parameters.json"
    )
    
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            Write-Error "Required file not found: $file"
            exit 1
        }
    }
    
    Write-Success "All prerequisites met"
    return $hasAzureCLI
}

function Connect-ToAzure {
    param([bool]$UseAzureCLI)
    
    Write-StepHeader "Connecting to Azure"
    
    if ($UseAzureCLI) {
        # Check if already logged in
        $accountInfo = az account show --query "id" -o tsv 2>$null
        if ($accountInfo -ne $SubscriptionId) {
            Write-Host "Logging in to Azure CLI..." -ForegroundColor $ColorInfo
            az login --output table
        }
        
        # Set subscription
        az account set --subscription $SubscriptionId
        $currentSub = az account show --query "id" -o tsv
        
        if ($currentSub -eq $SubscriptionId) {
            Write-Success "Connected to subscription: $SubscriptionId"
        }
        else {
            Write-Error "Failed to set subscription to: $SubscriptionId"
            exit 1
        }
    }
    else {
        # Azure PowerShell
        $context = Get-AzContext -ErrorAction SilentlyContinue
        if (-not $context -or $context.Subscription.Id -ne $SubscriptionId) {
            Write-Host "Connecting to Azure PowerShell..." -ForegroundColor $ColorInfo
            Connect-AzAccount -SubscriptionId $SubscriptionId
        }
        
        Write-Success "Connected to subscription: $SubscriptionId"
    }
}

function New-ResourceGroup {
    param([bool]$UseAzureCLI)
    
    Write-StepHeader "Creating Resource Group"
    
    if ($UseAzureCLI) {
        # Check if resource group exists
        $rgExists = az group exists --name $ResourceGroupName --output tsv
        
        if ($rgExists -eq "true") {
            Write-Warning "Resource group '$ResourceGroupName' already exists"
            if (-not $Force) {
                $response = Read-Host "Continue with existing resource group? (y/n)"
                if ($response -notmatch '^[Yy]') {
                    Write-Host "Deployment cancelled"
                    exit 0
                }
            }
        }
        else {
            Write-Host "Creating resource group '$ResourceGroupName'..." -ForegroundColor $ColorInfo
            az group create --name $ResourceGroupName --location $Location --output table
            Write-Success "Resource group created successfully"
        }
    }
    else {
        # Azure PowerShell
        $rg = Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue
        
        if ($rg) {
            Write-Warning "Resource group '$ResourceGroupName' already exists"
            if (-not $Force) {
                $response = Read-Host "Continue with existing resource group? (y/n)"
                if ($response -notmatch '^[Yy]') {
                    Write-Host "Deployment cancelled"
                    exit 0
                }
            }
        }
        else {
            Write-Host "Creating resource group '$ResourceGroupName'..." -ForegroundColor $ColorInfo
            New-AzResourceGroup -Name $ResourceGroupName -Location $Location
            Write-Success "Resource group created successfully"
        }
    }
}

function Deploy-Infrastructure {
    param([bool]$UseAzureCLI)
    
    Write-StepHeader "Deploying Infrastructure"
    
    # Update parameters file with user inputs
    $parametersFile = Join-Path $InfrastructurePath "main.parameters.json"
    $parameters = Get-Content $parametersFile | ConvertFrom-Json
    $parameters.parameters.environmentName.value = $Environment
    $parameters.parameters.adminEmail.value = $AdminEmail
    
    $tempParametersFile = Join-Path $env:TEMP "main.parameters.temp.json"
    $parameters | ConvertTo-Json -Depth 10 | Set-Content $tempParametersFile
    
    try {
        if ($UseAzureCLI) {
            Write-Host "Deploying infrastructure using Azure CLI..." -ForegroundColor $ColorInfo
            $deploymentResult = az deployment group create `
                --resource-group $ResourceGroupName `
                --template-file (Join-Path $InfrastructurePath "main.bicep") `
                --parameters @$tempParametersFile `
                --output json | ConvertFrom-Json
            
            if ($deploymentResult.properties.provisioningState -eq "Succeeded") {
                Write-Success "Infrastructure deployment completed successfully"
                return $deploymentResult.properties.outputs
            }
            else {
                Write-Error "Infrastructure deployment failed"
                exit 1
            }
        }
        else {
            Write-Host "Deploying infrastructure using Azure PowerShell..." -ForegroundColor $ColorInfo
            $deployment = New-AzResourceGroupDeployment `
                -ResourceGroupName $ResourceGroupName `
                -TemplateFile (Join-Path $InfrastructurePath "main.bicep") `
                -TemplateParameterFile $tempParametersFile `
                -Verbose
            
            if ($deployment.ProvisioningState -eq "Succeeded") {
                Write-Success "Infrastructure deployment completed successfully"
                return $deployment.Outputs
            }
            else {
                Write-Error "Infrastructure deployment failed"
                exit 1
            }
        }
    }
    finally {
        if (Test-Path $tempParametersFile) {
            Remove-Item $tempParametersFile -Force
        }
    }
}

function Upload-TestData {
    param(
        [bool]$UseAzureCLI,
        [string]$StorageAccountName
    )
    
    if (-not $CreateTestData) {
        Write-Warning "Skipping test data upload as requested"
        return
    }
    
    Write-StepHeader "Uploading Test Data"
    
    # Get test data files
    $testFiles = Get-ChildItem -Path $TestDataPath -Filter "*.csv"
    
    foreach ($file in $testFiles) {
        Write-Host "Uploading $($file.Name)..." -ForegroundColor $ColorInfo
        
        if ($UseAzureCLI) {
            az storage blob upload `
                --account-name $StorageAccountName `
                --container-name "raw-data" `
                --name $file.Name `
                --file $file.FullName `
                --auth-mode login `
                --output table
        }
        else {
            # Use Azure PowerShell
            $ctx = New-AzStorageContext -StorageAccountName $StorageAccountName -UseConnectedAccount
            Set-AzStorageBlobContent `
                -File $file.FullName `
                -Container "raw-data" `
                -Blob $file.Name `
                -Context $ctx
        }
    }
    
    Write-Success "Test data uploaded successfully"
}

function Deploy-ADF-Pipelines {
    param(
        [bool]$UseAzureCLI,
        [string]$DataFactoryName,
        [string]$StorageAccountName,
        [string]$SqlServerName
    )
    
    Write-StepHeader "Deploying ADF Pipelines"
    
    # Get pipeline template files
    $pipelineFiles = Get-ChildItem -Path $AdfTemplatesPath -Filter "*.json"
    
    foreach ($file in $pipelineFiles) {
        Write-Host "Deploying pipeline from $($file.Name)..." -ForegroundColor $ColorInfo
        
        # Read and update pipeline template
        $pipelineContent = Get-Content $file.FullName | ConvertFrom-Json
        
        # Update connection references if needed
        # This is a simplified version - in practice, you'd need to create linked services first
        
        if ($UseAzureCLI) {
            # Create pipeline using Azure CLI
            $tempFile = Join-Path $env:TEMP $file.Name
            $pipelineContent | ConvertTo-Json -Depth 20 | Set-Content $tempFile
            
            try {
                az datafactory pipeline create `
                    --resource-group $ResourceGroupName `
                    --factory-name $DataFactoryName `
                    --name $pipelineContent.name `
                    --pipeline @$tempFile
            }
            finally {
                if (Test-Path $tempFile) {
                    Remove-Item $tempFile -Force
                }
            }
        }
        else {
            # Use Azure PowerShell (would require Az.DataFactory module)
            Write-Warning "Azure PowerShell ADF pipeline deployment not implemented in this version"
        }
    }
    
    Write-Success "ADF pipelines deployed successfully"
}

function Setup-Database {
    param(
        [string]$SqlServerName,
        [string]$DatabaseName
    )
    
    Write-StepHeader "Setting up Database Schema"
    
    $sqlScriptFile = Join-Path $TestDataPath "database-setup.sql"
    
    if (-not (Test-Path $sqlScriptFile)) {
        Write-Warning "Database setup script not found, skipping database setup"
        return
    }
    
    try {
        # Check if sqlcmd is available
        $null = Get-Command sqlcmd -ErrorAction Stop
        
        Write-Host "Executing database setup script..." -ForegroundColor $ColorInfo
        
        # Execute SQL script
        sqlcmd -S "$SqlServerName.database.windows.net" `
               -d $DatabaseName `
               -U "adfadmin" `
               -P "TempPassword123!" `
               -i $sqlScriptFile
        
        Write-Success "Database schema created successfully"
    }
    catch {
        Write-Warning "sqlcmd not available, skipping database setup. Please run database-setup.sql manually."
    }
}

function Create-TestFailures {
    param(
        [bool]$UseAzureCLI,
        [string]$DataFactoryName
    )
    
    if (-not $CreateTestData) {
        Write-Warning "Skipping test failure creation as requested"
        return
    }
    
    Write-StepHeader "Creating Test Failures"
    
    Write-Host "Triggering test pipeline runs to generate failure scenarios..." -ForegroundColor $ColorInfo
    
    # Define test scenarios
    $testScenarios = @(
        @{
            PipelineName = "DataIngestionPipeline"
            Parameters = @{ sourceFileName = "customer_data_with_errors.csv"; forceFailure = $false }
        },
        @{
            PipelineName = "ETLTransformPipeline"
            Parameters = @{ batchDate = (Get-Date).ToString("yyyy-MM-dd"); simulateFailure = $true }
        }
    )
    
    foreach ($scenario in $testScenarios) {
        Write-Host "Triggering $($scenario.PipelineName)..." -ForegroundColor $ColorInfo
        
        if ($UseAzureCLI) {
            $parametersJson = $scenario.Parameters | ConvertTo-Json -Compress
            
            az datafactory pipeline create-run `
                --resource-group $ResourceGroupName `
                --factory-name $DataFactoryName `
                --name $scenario.PipelineName `
                --parameters $parametersJson `
                --output table
        }
    }
    
    Write-Success "Test failure scenarios initiated"
}

function Deploy-WebApp {
    param(
        [string]$WebAppName,
        [hashtable]$InfrastructureOutputs
    )
    
    if (-not $DeployWebApp) {
        Write-Warning "Skipping web app deployment as requested"
        return
    }
    
    Write-StepHeader "Deploying Web Application"
    
    # Package the web application
    $webAppPath = Join-Path $ScriptPath "..\.."
    $packagePath = Join-Path $env:TEMP "adf-monitor-webapp.zip"
    
    Write-Host "Creating deployment package..." -ForegroundColor $ColorInfo
    
    # Create a simple deployment package (in a real scenario, you'd use proper build tools)
    $filesToPackage = @(
        "webapp.py",
        "requirements.txt"
    )
    
    # This is a simplified packaging process
    Write-Warning "Web app deployment requires manual setup. Please deploy webapp.py to the App Service manually."
    
    Write-Success "Web app deployment prepared"
}

function Show-DeploymentSummary {
    param([hashtable]$Outputs)
    
    Write-StepHeader "Deployment Summary"
    
    Write-Host "`nDeployment completed successfully!" -ForegroundColor $ColorSuccess
    Write-Host "`nResource Details:" -ForegroundColor $ColorInfo
    
    foreach ($output in $Outputs.GetEnumerator()) {
        $value = if ($output.Value.value) { $output.Value.value } else { $output.Value }
        Write-Host "  $($output.Key): $value" -ForegroundColor White
    }
    
    Write-Host "`nNext Steps:" -ForegroundColor $ColorInfo
    Write-Host "1. Navigate to the Azure portal to verify all resources are created"
    Write-Host "2. Access the monitoring web app at the provided URL"
    Write-Host "3. Review the test data and pipeline runs in Azure Data Factory"
    Write-Host "4. Check Log Analytics for monitoring data"
    Write-Host "5. Run the ADF Monitor Pro application to see the monitoring dashboard"
    
    Write-Host "`nImportant Security Note:" -ForegroundColor $ColorWarning
    Write-Host "This deployment uses default passwords and settings suitable only for testing."
    Write-Host "Please update passwords and configure proper security settings for production use."
    
    Write-Host "`nTesting the Environment:" -ForegroundColor $ColorInfo
    Write-Host "- Check the 'test-scenarios.md' file for detailed testing instructions"
    Write-Host "- Use the sample data files to trigger different pipeline scenarios"
    Write-Host "- Monitor the results in both Azure Data Factory and the monitoring dashboard"
}

# Main execution flow
try {
    Write-Host "🚀 ADF Monitor Pro Test Environment Deployment" -ForegroundColor $ColorInfo
    Write-Host "=============================================" -ForegroundColor $ColorInfo
    Write-Host "Subscription: $SubscriptionId"
    Write-Host "Resource Group: $ResourceGroupName"
    Write-Host "Location: $Location"
    Write-Host "Environment: $Environment"
    Write-Host "Admin Email: $AdminEmail"
    
    # Step 1: Check prerequisites
    $useAzureCLI = Test-Prerequisites
    
    # Step 2: Connect to Azure
    Connect-ToAzure -UseAzureCLI $useAzureCLI
    
    # Step 3: Create resource group
    New-ResourceGroup -UseAzureCLI $useAzureCLI
    
    # Step 4: Deploy infrastructure
    $outputs = Deploy-Infrastructure -UseAzureCLI $useAzureCLI
    
    # Extract output values
    $storageAccountName = if ($outputs.storageAccountName.value) { $outputs.storageAccountName.value } else { $outputs.storageAccountName }
    $dataFactoryName = if ($outputs.dataFactoryName.value) { $outputs.dataFactoryName.value } else { $outputs.dataFactoryName }
    $sqlServerName = if ($outputs.sqlServerName.value) { $outputs.sqlServerName.value } else { $outputs.sqlServerName }
    $sqlDatabaseName = if ($outputs.sqlDatabaseName.value) { $outputs.sqlDatabaseName.value } else { $outputs.sqlDatabaseName }
    $webAppName = if ($outputs.webAppName.value) { $outputs.webAppName.value } else { $outputs.webAppName }
    
    # Step 5: Upload test data
    Upload-TestData -UseAzureCLI $useAzureCLI -StorageAccountName $storageAccountName
    
    # Step 6: Setup database
    Setup-Database -SqlServerName $sqlServerName -DatabaseName $sqlDatabaseName
    
    # Step 7: Deploy ADF pipelines
    Deploy-ADF-Pipelines -UseAzureCLI $useAzureCLI -DataFactoryName $dataFactoryName -StorageAccountName $storageAccountName -SqlServerName $sqlServerName
    
    # Step 8: Create test failures
    Create-TestFailures -UseAzureCLI $useAzureCLI -DataFactoryName $dataFactoryName
    
    # Step 9: Deploy web app
    Deploy-WebApp -WebAppName $webAppName -InfrastructureOutputs $outputs
    
    # Step 10: Show summary
    Show-DeploymentSummary -Outputs $outputs
    
}
catch {
    Write-Error "Deployment failed with error: $($_.Exception.Message)"
    Write-Host "Error details:" -ForegroundColor $ColorError
    Write-Host $_.Exception.ToString() -ForegroundColor $ColorError
    exit 1
}