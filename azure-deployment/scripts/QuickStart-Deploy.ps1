#!/usr/bin/env pwsh
#Requires -Version 7.0

<#
.SYNOPSIS
    Quick Start deployment for ADF Monitor Pro test environment

.DESCRIPTION
    This script provides a simplified deployment experience with minimal prompts.
    Perfect for getting started quickly with default settings.

.EXAMPLE
    .\QuickStart-Deploy.ps1

.NOTES
    This script will prompt for required information and deploy with sensible defaults.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [switch]$UseDefaults,
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipPrerequisiteCheck
)

# Colors for output
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"
$ColorPrompt = "Magenta"

function Write-Banner {
    Clear-Host
    Write-Host @"
    
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              🚀 ADF Monitor Pro Quick Deploy 🚀              ║
    ║                                                              ║
    ║                One-Click Azure Test Environment              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
"@ -ForegroundColor $ColorInfo
}

function Get-UserInputs {
    Write-Host "`n📝 Setup Configuration" -ForegroundColor $ColorInfo
    Write-Host "======================" -ForegroundColor $ColorInfo
    
    # Get subscription ID
    $subscriptionId = ""
    if (-not $UseDefaults) {
        while ([string]::IsNullOrWhiteSpace($subscriptionId) -or $subscriptionId.Length -ne 36) {
            $subscriptionId = Read-Host -Prompt "Enter your Azure Subscription ID (36 characters)"
            if ([string]::IsNullOrWhiteSpace($subscriptionId)) {
                Write-Host "❌ Subscription ID is required!" -ForegroundColor $ColorError
            }
            elseif ($subscriptionId.Length -ne 36) {
                Write-Host "❌ Invalid subscription ID format! Should be 36 characters." -ForegroundColor $ColorError
            }
        }
    }
    else {
        $subscriptionId = "12345678-1234-1234-1234-123456789012"
        Write-Host "Using default subscription ID (you'll need to change this)" -ForegroundColor $ColorWarning
    }
    
    # Get admin email
    $adminEmail = ""
    if (-not $UseDefaults) {
        while ([string]::IsNullOrWhiteSpace($adminEmail) -or $adminEmail -notmatch '^[^@]+@[^@]+\.[^@]+$') {
            $adminEmail = Read-Host -Prompt "Enter your admin email address"
            if ([string]::IsNullOrWhiteSpace($adminEmail)) {
                Write-Host "❌ Email address is required!" -ForegroundColor $ColorError
            }
            elseif ($adminEmail -notmatch '^[^@]+@[^@]+\.[^@]+$') {
                Write-Host "❌ Invalid email format!" -ForegroundColor $ColorError
            }
        }
    }
    else {
        $adminEmail = "admin@company.com"
    }
    
    # Get resource group name
    $resourceGroupName = "adf-monitor-quickstart-rg"
    if (-not $UseDefaults) {
        $rgInput = Read-Host -Prompt "Enter resource group name (press Enter for '$resourceGroupName')"
        if (-not [string]::IsNullOrWhiteSpace($rgInput)) {
            $resourceGroupName = $rgInput
        }
    }
    
    # Get region
    $location = "East US"
    if (-not $UseDefaults) {
        Write-Host "`nAvailable regions: East US, West US 2, Central US, West Europe, North Europe" -ForegroundColor $ColorInfo
        $locationInput = Read-Host -Prompt "Enter Azure region (press Enter for '$location')"
        if (-not [string]::IsNullOrWhiteSpace($locationInput)) {
            $location = $locationInput
        }
    }
    
    return @{
        SubscriptionId = $subscriptionId
        AdminEmail = $adminEmail
        ResourceGroupName = $resourceGroupName
        Location = $location
    }
}

function Test-QuickPrerequisites {
    if ($SkipPrerequisiteCheck) {
        Write-Host "⏩ Skipping prerequisite check as requested" -ForegroundColor $ColorWarning
        return $true
    }
    
    Write-Host "`n🔍 Checking Prerequisites" -ForegroundColor $ColorInfo
    Write-Host "========================" -ForegroundColor $ColorInfo
    
    $hasAzureCLI = $false
    $hasAzurePowerShell = $false
    
    # Check Azure CLI
    try {
        $null = Get-Command az -ErrorAction Stop
        $version = az version --query '"azure-cli"' -o tsv
        Write-Host "✅ Azure CLI found (version $version)" -ForegroundColor $ColorSuccess
        $hasAzureCLI = $true
    }
    catch {
        Write-Host "❌ Azure CLI not found" -ForegroundColor $ColorError
    }
    
    # Check Azure PowerShell
    try {
        $azModule = Get-Module -Name Az -ListAvailable -ErrorAction Stop | Select-Object -First 1
        if ($azModule) {
            Write-Host "✅ Azure PowerShell found (version $($azModule.Version))" -ForegroundColor $ColorSuccess
            $hasAzurePowerShell = $true
        }
    }
    catch {
        Write-Host "❌ Azure PowerShell not found" -ForegroundColor $ColorError
    }
    
    if (-not $hasAzureCLI -and -not $hasAzurePowerShell) {
        Write-Host "`n❌ Prerequisites Missing!" -ForegroundColor $ColorError
        Write-Host "You need either Azure CLI or Azure PowerShell installed." -ForegroundColor $ColorError
        Write-Host "`nInstallation options:" -ForegroundColor $ColorInfo
        Write-Host "1. Azure CLI: https://aka.ms/installazurecliwindows" -ForegroundColor White
        Write-Host "2. Azure PowerShell: Install-Module -Name Az -Repository PSGallery" -ForegroundColor White
        
        $response = Read-Host "`nDo you want to continue anyway? (y/n)"
        return $response -match '^[Yy]'
    }
    
    Write-Host "✅ Prerequisites check passed!" -ForegroundColor $ColorSuccess
    return $true
}

function Show-DeploymentSummary {
    param($Config)
    
    Write-Host "`n📋 Deployment Summary" -ForegroundColor $ColorInfo
    Write-Host "=====================" -ForegroundColor $ColorInfo
    Write-Host "Subscription ID: $($Config.SubscriptionId)" -ForegroundColor White
    Write-Host "Resource Group: $($Config.ResourceGroupName)" -ForegroundColor White
    Write-Host "Location: $($Config.Location)" -ForegroundColor White
    Write-Host "Admin Email: $($Config.AdminEmail)" -ForegroundColor White
    Write-Host "Environment: Development (quick start)" -ForegroundColor White
    
    Write-Host "`n🚀 What will be deployed:" -ForegroundColor $ColorInfo
    Write-Host "• Azure Data Factory with sample pipelines" -ForegroundColor White
    Write-Host "• Storage Account with test data" -ForegroundColor White
    Write-Host "• SQL Database with sample schema" -ForegroundColor White
    Write-Host "• Key Vault for secrets" -ForegroundColor White
    Write-Host "• Log Analytics for monitoring" -ForegroundColor White
    Write-Host "• App Service for web application" -ForegroundColor White
    
    Write-Host "`n💰 Estimated cost: $50-100/month for development usage" -ForegroundColor $ColorWarning
    
    if (-not $UseDefaults) {
        $confirmation = Read-Host "`nProceed with deployment? (y/n)"
        return $confirmation -match '^[Yy]'
    }
    
    return $true
}

function Invoke-QuickDeploy {
    param($Config)
    
    Write-Host "`n🚀 Starting Deployment" -ForegroundColor $ColorInfo
    Write-Host "=====================" -ForegroundColor $ColorInfo
    
    $scriptPath = Join-Path $PSScriptRoot "Deploy-ADF-Monitor-Test-Environment.ps1"
    
    if (-not (Test-Path $scriptPath)) {
        Write-Host "❌ Main deployment script not found at: $scriptPath" -ForegroundColor $ColorError
        Write-Host "Please ensure you're running this script from the correct directory." -ForegroundColor $ColorError
        return $false
    }
    
    try {
        $deployParams = @{
            SubscriptionId = $Config.SubscriptionId
            ResourceGroupName = $Config.ResourceGroupName
            Location = $Config.Location
            Environment = "dev"
            AdminEmail = $Config.AdminEmail
            DeployWebApp = $true
            CreateTestData = $true
            Force = $UseDefaults
        }
        
        Write-Host "Calling main deployment script..." -ForegroundColor $ColorInfo
        & $scriptPath @deployParams
        
        return $true
    }
    catch {
        Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor $ColorError
        return $false
    }
}

function Show-NextSteps {
    Write-Host "`n🎉 Quick Start Complete!" -ForegroundColor $ColorSuccess
    Write-Host "========================" -ForegroundColor $ColorSuccess
    
    Write-Host "`n📚 Next Steps:" -ForegroundColor $ColorInfo
    Write-Host "1. Open Azure Portal and navigate to your resource group" -ForegroundColor White
    Write-Host "2. Explore the deployed Azure Data Factory pipelines" -ForegroundColor White
    Write-Host "3. Run the ADF Monitor Pro application (webapp.py)" -ForegroundColor White
    Write-Host "4. Test different monitoring scenarios using the sample data" -ForegroundColor White
    Write-Host "5. Review the README.md file for detailed usage instructions" -ForegroundColor White
    
    Write-Host "`n🔗 Useful Links:" -ForegroundColor $ColorInfo
    Write-Host "• Azure Portal: https://portal.azure.com" -ForegroundColor White
    Write-Host "• ADF Monitor Pro Documentation: See README.md" -ForegroundColor White
    Write-Host "• Test Scenarios: See test-scenarios.md" -ForegroundColor White
    
    Write-Host "`n⚠️  Important Reminders:" -ForegroundColor $ColorWarning
    Write-Host "• This is a TEST environment - change passwords for production use" -ForegroundColor White
    Write-Host "• Monitor your Azure costs using Azure Cost Management" -ForegroundColor White
    Write-Host "• Clean up resources when done to avoid ongoing charges" -ForegroundColor White
}

# Main execution
try {
    Write-Banner
    
    if (-not (Test-QuickPrerequisites)) {
        Write-Host "`n❌ Prerequisites not met. Exiting..." -ForegroundColor $ColorError
        exit 1
    }
    
    $config = Get-UserInputs
    
    if (-not (Show-DeploymentSummary -Config $config)) {
        Write-Host "`n❌ Deployment cancelled by user." -ForegroundColor $ColorWarning
        exit 0
    }
    
    $success = Invoke-QuickDeploy -Config $config
    
    if ($success) {
        Show-NextSteps
    }
    else {
        Write-Host "`n❌ Quick start deployment failed. Check the error messages above." -ForegroundColor $ColorError
        exit 1
    }
}
catch {
    Write-Host "`n❌ Quick start failed with error: $($_.Exception.Message)" -ForegroundColor $ColorError
    Write-Host "Error details:" -ForegroundColor $ColorError
    Write-Host $_.Exception.ToString() -ForegroundColor $ColorError
    exit 1
}