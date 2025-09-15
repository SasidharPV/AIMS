#Requires -Version 7.0

<#
.SYNOPSIS
    Validates the deployed ADF Monitor Pro test environment

.DESCRIPTION
    This script validates that all Azure resources are correctly deployed and configured.
    It checks resource status, connectivity, and basic functionality.

.PARAMETER ResourceGroupName
    Name of the resource group containing the deployed resources

.PARAMETER SubscriptionId
    Azure subscription ID where resources were deployed

.EXAMPLE
    .\Validate-Deployment.ps1 -ResourceGroupName "adf-monitor-test-rg" -SubscriptionId "your-subscription-id"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId
)

$ErrorActionPreference = "Continue"
$WarningPreference = "Continue"

# Colors for output
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"

function Write-ValidationHeader {
    param([string]$Message)
    Write-Host "`n🔍 $Message" -ForegroundColor $ColorInfo
    Write-Host ("=" * ($Message.Length + 3)) -ForegroundColor $ColorInfo
}

function Write-TestResult {
    param(
        [string]$TestName,
        [bool]$Passed,
        [string]$Details = ""
    )
    
    $status = if ($Passed) { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($Passed) { $ColorSuccess } else { $ColorError }
    
    Write-Host "$status - $TestName" -ForegroundColor $color
    if ($Details) {
        Write-Host "    $Details" -ForegroundColor White
    }
    
    return $Passed
}

function Test-AzureConnection {
    Write-ValidationHeader "Testing Azure Connection"
    
    try {
        # Test Azure CLI connection
        $currentSub = az account show --query "id" -o tsv 2>$null
        if ($currentSub -eq $SubscriptionId) {
            Write-TestResult "Azure CLI Connection" $true "Connected to subscription: $SubscriptionId"
            return $true
        }
        else {
            Write-TestResult "Azure CLI Connection" $false "Current subscription ($currentSub) doesn't match target ($SubscriptionId)"
            return $false
        }
    }
    catch {
        Write-TestResult "Azure CLI Connection" $false "Error: $($_.Exception.Message)"
        return $false
    }
}

function Test-ResourceGroup {
    Write-ValidationHeader "Testing Resource Group"
    
    try {
        $rg = az group show --name $ResourceGroupName --query "name" -o tsv 2>$null
        if ($rg -eq $ResourceGroupName) {
            Write-TestResult "Resource Group Exists" $true "Found resource group: $ResourceGroupName"
            return $true
        }
        else {
            Write-TestResult "Resource Group Exists" $false "Resource group not found: $ResourceGroupName"
            return $false
        }
    }
    catch {
        Write-TestResult "Resource Group Exists" $false "Error: $($_.Exception.Message)"
        return $false
    }
}

function Test-CoreResources {
    Write-ValidationHeader "Testing Core Resources"
    
    $expectedResources = @(
        @{ Type = "Microsoft.DataFactory/factories"; Name = "Data Factory" },
        @{ Type = "Microsoft.Storage/storageAccounts"; Name = "Storage Account" },
        @{ Type = "Microsoft.Sql/servers"; Name = "SQL Server" },
        @{ Type = "Microsoft.Sql/servers/databases"; Name = "SQL Database" },
        @{ Type = "Microsoft.KeyVault/vaults"; Name = "Key Vault" },
        @{ Type = "Microsoft.OperationalInsights/workspaces"; Name = "Log Analytics Workspace" },
        @{ Type = "Microsoft.Web/serverfarms"; Name = "App Service Plan" },
        @{ Type = "Microsoft.Web/sites"; Name = "App Service" }
    )
    
    $allPassed = $true
    
    foreach ($resource in $expectedResources) {
        try {
            $resources = az resource list --resource-group $ResourceGroupName --resource-type $resource.Type --query "[].name" -o tsv 2>$null
            
            if ($resources) {
                Write-TestResult "$($resource.Name)" $true "Found: $($resources -join ', ')"
            }
            else {
                Write-TestResult "$($resource.Name)" $false "No resources of type $($resource.Type) found"
                $allPassed = $false
            }
        }
        catch {
            Write-TestResult "$($resource.Name)" $false "Error checking resource: $($_.Exception.Message)"
            $allPassed = $false
        }
    }
    
    return $allPassed
}

function Test-StorageAccount {
    Write-ValidationHeader "Testing Storage Account"
    
    try {
        # Get storage account name
        $storageAccounts = az storage account list --resource-group $ResourceGroupName --query "[].name" -o tsv 2>$null
        
        if (-not $storageAccounts) {
            Write-TestResult "Storage Account Access" $false "No storage accounts found"
            return $false
        }
        
        $storageAccountName = $storageAccounts.Split("`n")[0]
        Write-TestResult "Storage Account Found" $true "Using: $storageAccountName"
        
        # Test container access
        $containers = az storage container list --account-name $storageAccountName --auth-mode login --query "[].name" -o tsv 2>$null
        
        if ($containers) {
            Write-TestResult "Storage Containers" $true "Found containers: $($containers -replace "`n", ', ')"
            
            # Test if test data exists
            $blobs = az storage blob list --account-name $storageAccountName --container-name "raw-data" --auth-mode login --query "[].name" -o tsv 2>$null
            
            if ($blobs) {
                Write-TestResult "Test Data Upload" $true "Found test files: $($blobs -replace "`n", ', ')"
            }
            else {
                Write-TestResult "Test Data Upload" $false "No test data files found in raw-data container"
            }
        }
        else {
            Write-TestResult "Storage Containers" $false "Unable to list containers (permissions issue?)"
        }
        
        return $true
    }
    catch {
        Write-TestResult "Storage Account Access" $false "Error: $($_.Exception.Message)"
        return $false
    }
}

function Test-DataFactory {
    Write-ValidationHeader "Testing Data Factory"
    
    try {
        # Get ADF name
        $adfNames = az datafactory list --resource-group $ResourceGroupName --query "[].name" -o tsv 2>$null
        
        if (-not $adfNames) {
            Write-TestResult "Data Factory Access" $false "No Data Factory found"
            return $false
        }
        
        $adfName = $adfNames.Split("`n")[0]
        Write-TestResult "Data Factory Found" $true "Using: $adfName"
        
        # Test pipelines
        $pipelines = az datafactory pipeline list --resource-group $ResourceGroupName --factory-name $adfName --query "[].name" -o tsv 2>$null
        
        if ($pipelines) {
            Write-TestResult "ADF Pipelines" $true "Found pipelines: $($pipelines -replace "`n", ', ')"
        }
        else {
            Write-TestResult "ADF Pipelines" $false "No pipelines found in Data Factory"
        }
        
        # Test linked services
        $linkedServices = az datafactory linked-service list --resource-group $ResourceGroupName --factory-name $adfName --query "[].name" -o tsv 2>$null
        
        if ($linkedServices) {
            Write-TestResult "Linked Services" $true "Found linked services: $($linkedServices -replace "`n", ', ')"
        }
        else {
            Write-TestResult "Linked Services" $false "No linked services found"
        }
        
        return $true
    }
    catch {
        Write-TestResult "Data Factory Access" $false "Error: $($_.Exception.Message)"
        return $false
    }
}

function Test-SqlDatabase {
    Write-ValidationHeader "Testing SQL Database"
    
    try {
        # Get SQL server name
        $sqlServers = az sql server list --resource-group $ResourceGroupName --query "[].name" -o tsv 2>$null
        
        if (-not $sqlServers) {
            Write-TestResult "SQL Server Access" $false "No SQL Server found"
            return $false
        }
        
        $sqlServerName = $sqlServers.Split("`n")[0]
        Write-TestResult "SQL Server Found" $true "Using: $sqlServerName"
        
        # Test databases
        $databases = az sql db list --resource-group $ResourceGroupName --server $sqlServerName --query "[?name!='master'].name" -o tsv 2>$null
        
        if ($databases) {
            Write-TestResult "SQL Database" $true "Found databases: $($databases -replace "`n", ', ')"
            
            # Test connectivity (basic check)
            try {
                $connectionTest = az sql db show --resource-group $ResourceGroupName --server $sqlServerName --name $databases.Split("`n")[0] --query "status" -o tsv 2>$null
                
                if ($connectionTest -eq "Online") {
                    Write-TestResult "Database Status" $true "Database is online and accessible"
                }
                else {
                    Write-TestResult "Database Status" $false "Database status: $connectionTest"
                }
            }
            catch {
                Write-TestResult "Database Status" $false "Unable to check database status"
            }
        }
        else {
            Write-TestResult "SQL Database" $false "No user databases found"
        }
        
        return $true
    }
    catch {
        Write-TestResult "SQL Database Access" $false "Error: $($_.Exception.Message)"
        return $false
    }
}

function Test-KeyVault {
    Write-ValidationHeader "Testing Key Vault"
    
    try {
        # Get Key Vault name
        $kvNames = az keyvault list --resource-group $ResourceGroupName --query "[].name" -o tsv 2>$null
        
        if (-not $kvNames) {
            Write-TestResult "Key Vault Access" $false "No Key Vault found"
            return $false
        }
        
        $kvName = $kvNames.Split("`n")[0]
        Write-TestResult "Key Vault Found" $true "Using: $kvName"
        
        # Test access permissions
        try {
            $secrets = az keyvault secret list --vault-name $kvName --query "[].name" -o tsv 2>$null
            Write-TestResult "Key Vault Access" $true "Successfully accessed Key Vault secrets"
        }
        catch {
            Write-TestResult "Key Vault Access" $false "Unable to access Key Vault (permissions issue?)"
        }
        
        return $true
    }
    catch {
        Write-TestResult "Key Vault Access" $false "Error: $($_.Exception.Message)"
        return $false
    }
}

function Test-LogAnalytics {
    Write-ValidationHeader "Testing Log Analytics"
    
    try {
        # Get Log Analytics workspace name
        $workspaces = az monitor log-analytics workspace list --resource-group $ResourceGroupName --query "[].name" -o tsv 2>$null
        
        if (-not $workspaces) {
            Write-TestResult "Log Analytics Workspace" $false "No Log Analytics workspace found"
            return $false
        }
        
        $workspaceName = $workspaces.Split("`n")[0]
        Write-TestResult "Log Analytics Workspace" $true "Found: $workspaceName"
        
        # Test basic functionality
        try {
            $workspaceInfo = az monitor log-analytics workspace show --resource-group $ResourceGroupName --workspace-name $workspaceName --query "provisioningState" -o tsv 2>$null
            
            if ($workspaceInfo -eq "Succeeded") {
                Write-TestResult "Workspace Status" $true "Workspace is successfully provisioned"
            }
            else {
                Write-TestResult "Workspace Status" $false "Workspace status: $workspaceInfo"
            }
        }
        catch {
            Write-TestResult "Workspace Status" $false "Unable to check workspace status"
        }
        
        return $true
    }
    catch {
        Write-TestResult "Log Analytics Access" $false "Error: $($_.Exception.Message)"
        return $false
    }
}

function Show-ValidationSummary {
    param([array]$TestResults)
    
    Write-Host "`n" -NoNewline
    Write-Host "📊 Validation Summary" -ForegroundColor $ColorInfo
    Write-Host "===================" -ForegroundColor $ColorInfo
    
    $passed = ($TestResults | Where-Object { $_ -eq $true }).Count
    $total = $TestResults.Count
    $failed = $total - $passed
    
    Write-Host "Total Tests: $total" -ForegroundColor White
    Write-Host "Passed: $passed" -ForegroundColor $ColorSuccess
    Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -eq 0) { $ColorSuccess } else { $ColorError })
    
    $percentage = [math]::Round(($passed / $total) * 100, 1)
    Write-Host "Success Rate: $percentage%" -ForegroundColor $(if ($percentage -gt 80) { $ColorSuccess } elseif ($percentage -gt 60) { $ColorWarning } else { $ColorError })
    
    if ($failed -eq 0) {
        Write-Host "`n🎉 All validations passed! Your environment is ready to use." -ForegroundColor $ColorSuccess
    }
    elseif ($failed -le 2) {
        Write-Host "`n⚠️  Minor issues detected. The environment should be mostly functional." -ForegroundColor $ColorWarning
        Write-Host "Review the failed tests and address any critical issues." -ForegroundColor $ColorWarning
    }
    else {
        Write-Host "`n❌ Multiple issues detected. Please review and fix the failed tests." -ForegroundColor $ColorError
        Write-Host "The environment may not function properly until these issues are resolved." -ForegroundColor $ColorError
    }
}

# Main execution
try {
    Write-Host "🔍 ADF Monitor Pro Deployment Validation" -ForegroundColor $ColorInfo
    Write-Host "=========================================" -ForegroundColor $ColorInfo
    Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor White
    Write-Host "Subscription: $SubscriptionId" -ForegroundColor White
    
    $testResults = @()
    
    # Run all validation tests
    $testResults += Test-AzureConnection
    $testResults += Test-ResourceGroup
    $testResults += Test-CoreResources
    $testResults += Test-StorageAccount
    $testResults += Test-DataFactory
    $testResults += Test-SqlDatabase
    $testResults += Test-KeyVault
    $testResults += Test-LogAnalytics
    
    # Show summary
    Show-ValidationSummary -TestResults $testResults
    
    # Exit with appropriate code
    $failedTests = ($testResults | Where-Object { $_ -eq $false }).Count
    exit $failedTests
}
catch {
    Write-Host "`n❌ Validation failed with error: $($_.Exception.Message)" -ForegroundColor $ColorError
    Write-Host "Error details:" -ForegroundColor $ColorError
    Write-Host $_.Exception.ToString() -ForegroundColor $ColorError
    exit 1
}