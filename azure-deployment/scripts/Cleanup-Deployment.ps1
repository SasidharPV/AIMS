#Requires -Version 7.0

<#
.SYNOPSIS
    Cleanup script for ADF Monitor Pro test environment

.DESCRIPTION
    This script safely removes all Azure resources created by the ADF Monitor Pro deployment.
    It provides options for selective cleanup and includes safety checks to prevent accidental deletion.

.PARAMETER ResourceGroupName
    Name of the resource group to clean up

.PARAMETER SubscriptionId
    Azure subscription ID where resources are deployed

.PARAMETER Force
    Skip confirmation prompts (use with caution!)

.PARAMETER SelectiveCleanup
    Only remove specific resource types instead of the entire resource group

.PARAMETER WhatIf
    Show what would be deleted without actually deleting anything

.EXAMPLE
    .\Cleanup-Deployment.ps1 -ResourceGroupName "adf-monitor-test-rg" -SubscriptionId "your-subscription-id"

.EXAMPLE
    .\Cleanup-Deployment.ps1 -ResourceGroupName "adf-monitor-test-rg" -SubscriptionId "your-subscription-id" -SelectiveCleanup

.EXAMPLE
    .\Cleanup-Deployment.ps1 -ResourceGroupName "adf-monitor-test-rg" -SubscriptionId "your-subscription-id" -WhatIf
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory = $false)]
    [switch]$Force,
    
    [Parameter(Mandatory = $false)]
    [switch]$SelectiveCleanup,
    
    [Parameter(Mandatory = $false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

# Colors for output
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"

function Write-CleanupHeader {
    param([string]$Message)
    Write-Host "`n🧹 $Message" -ForegroundColor $ColorInfo
    Write-Host ("=" * ($Message.Length + 3)) -ForegroundColor $ColorInfo
}

function Write-CleanupResult {
    param(
        [string]$Action,
        [bool]$Success,
        [string]$Details = ""
    )
    
    $status = if ($Success) { "✅ SUCCESS" } else { "❌ FAILED" }
    $color = if ($Success) { $ColorSuccess } else { $ColorError }
    
    Write-Host "$status - $Action" -ForegroundColor $color
    if ($Details) {
        Write-Host "    $Details" -ForegroundColor White
    }
}

function Test-AzureConnection {
    Write-CleanupHeader "Verifying Azure Connection"
    
    try {
        $currentSub = az account show --query "id" -o tsv 2>$null
        if ($currentSub -eq $SubscriptionId) {
            Write-CleanupResult "Azure Connection" $true "Connected to subscription: $SubscriptionId"
            return $true
        }
        else {
            Write-Host "❌ Current subscription ($currentSub) doesn't match target ($SubscriptionId)" -ForegroundColor $ColorError
            Write-Host "Please run: az account set --subscription $SubscriptionId" -ForegroundColor $ColorWarning
            return $false
        }
    }
    catch {
        Write-CleanupResult "Azure Connection" $false "Error: $($_.Exception.Message)"
        return $false
    }
}

function Get-ResourceGroupInfo {
    Write-CleanupHeader "Analyzing Resource Group"
    
    try {
        # Check if resource group exists
        $rg = az group show --name $ResourceGroupName --output json 2>$null | ConvertFrom-Json
        
        if (-not $rg) {
            Write-Host "❌ Resource group '$ResourceGroupName' not found!" -ForegroundColor $ColorError
            return $null
        }
        
        Write-CleanupResult "Resource Group Found" $true "Location: $($rg.location), Status: $($rg.properties.provisioningState)"
        
        # Get all resources in the resource group
        $resources = az resource list --resource-group $ResourceGroupName --output json 2>$null | ConvertFrom-Json
        
        if ($resources) {
            Write-Host "`n📋 Resources found:" -ForegroundColor $ColorInfo
            $resourceCount = @{}
            
            foreach ($resource in $resources) {
                $type = $resource.type
                if ($resourceCount.ContainsKey($type)) {
                    $resourceCount[$type]++
                }
                else {
                    $resourceCount[$type] = 1
                }
                
                Write-Host "  • $($resource.name) ($($resource.type))" -ForegroundColor White
            }
            
            Write-Host "`n📊 Resource Summary:" -ForegroundColor $ColorInfo
            foreach ($type in $resourceCount.Keys | Sort-Object) {
                Write-Host "  • $type: $($resourceCount[$type])" -ForegroundColor White
            }
            
            Write-Host "`nTotal resources: $($resources.Count)" -ForegroundColor White
        }
        else {
            Write-Host "📋 No resources found in resource group" -ForegroundColor $ColorWarning
        }
        
        return @{
            ResourceGroup = $rg
            Resources = $resources
        }
    }
    catch {
        Write-CleanupResult "Resource Group Analysis" $false "Error: $($_.Exception.Message)"
        return $null
    }
}

function Confirm-Deletion {
    param(
        [array]$Resources,
        [string]$ResourceGroupName
    )
    
    if ($Force) {
        Write-Host "⚠️  Force mode enabled - skipping confirmations" -ForegroundColor $ColorWarning
        return $true
    }
    
    Write-Host "`n⚠️  DELETION WARNING" -ForegroundColor $ColorWarning
    Write-Host "===================" -ForegroundColor $ColorWarning
    Write-Host "This action will permanently delete the following:" -ForegroundColor $ColorWarning
    
    if ($SelectiveCleanup) {
        Write-Host "• Selected resources in resource group: $ResourceGroupName" -ForegroundColor White
    }
    else {
        Write-Host "• ENTIRE resource group: $ResourceGroupName" -ForegroundColor White
        Write-Host "• ALL $($Resources.Count) resources within it" -ForegroundColor White
        Write-Host "• ALL data, configurations, and settings" -ForegroundColor White
    }
    
    Write-Host "`n💰 This will also stop all associated costs." -ForegroundColor $ColorInfo
    Write-Host "`n❗ This action CANNOT be undone!" -ForegroundColor $ColorError
    
    Write-Host "`nPlease type 'DELETE' to confirm (case-sensitive):" -ForegroundColor $ColorWarning -NoNewline
    $confirmation = Read-Host
    
    return $confirmation -ceq "DELETE"
}

function Remove-SelectiveResources {
    param([array]$Resources)
    
    Write-CleanupHeader "Selective Resource Cleanup"
    
    $resourceTypes = @(
        @{ Type = "Microsoft.DataFactory/factories"; Name = "Data Factory"; Priority = 1 },
        @{ Type = "Microsoft.Web/sites"; Name = "App Service"; Priority = 2 },
        @{ Type = "Microsoft.Web/serverfarms"; Name = "App Service Plan"; Priority = 3 },
        @{ Type = "Microsoft.Sql/servers/databases"; Name = "SQL Database"; Priority = 4 },
        @{ Type = "Microsoft.Sql/servers"; Name = "SQL Server"; Priority = 5 },
        @{ Type = "Microsoft.Storage/storageAccounts"; Name = "Storage Account"; Priority = 6 },
        @{ Type = "Microsoft.KeyVault/vaults"; Name = "Key Vault"; Priority = 7 },
        @{ Type = "Microsoft.OperationalInsights/workspaces"; Name = "Log Analytics"; Priority = 8 },
        @{ Type = "Microsoft.Insights/components"; Name = "Application Insights"; Priority = 9 }
    )
    
    Write-Host "Select resources to delete:" -ForegroundColor $ColorInfo
    
    $selectedTypes = @()
    for ($i = 0; $i -lt $resourceTypes.Count; $i++) {
        $resourceType = $resourceTypes[$i]
        $matchingResources = $Resources | Where-Object { $_.type -eq $resourceType.Type }
        
        if ($matchingResources) {
            $response = Read-Host "Delete $($resourceType.Name)? ($($matchingResources.Count) found) (y/n)"
            if ($response -match '^[Yy]') {
                $selectedTypes += $resourceType
            }
        }
    }
    
    if ($selectedTypes.Count -eq 0) {
        Write-Host "❌ No resources selected for deletion" -ForegroundColor $ColorWarning
        return
    }
    
    # Sort by priority to handle dependencies
    $selectedTypes = $selectedTypes | Sort-Object Priority
    
    foreach ($resourceType in $selectedTypes) {
        $matchingResources = $Resources | Where-Object { $_.type -eq $resourceType.Type }
        
        foreach ($resource in $matchingResources) {
            try {
                if ($WhatIf) {
                    Write-Host "[WHAT-IF] Would delete: $($resource.name) ($($resource.type))" -ForegroundColor $ColorInfo
                }
                else {
                    Write-Host "Deleting $($resource.name)..." -ForegroundColor $ColorInfo
                    
                    az resource delete --resource-group $ResourceGroupName --name $resource.name --resource-type $resource.type --output none
                    
                    Write-CleanupResult "Deleted $($resourceType.Name)" $true $resource.name
                }
            }
            catch {
                Write-CleanupResult "Delete $($resourceType.Name)" $false "Error deleting $($resource.name): $($_.Exception.Message)"
            }
        }
    }
}

function Remove-EntireResourceGroup {
    Write-CleanupHeader "Complete Resource Group Deletion"
    
    try {
        if ($WhatIf) {
            Write-Host "[WHAT-IF] Would delete entire resource group: $ResourceGroupName" -ForegroundColor $ColorInfo
            Write-CleanupResult "Resource Group Deletion (What-If)" $true "Would delete $ResourceGroupName and all its resources"
        }
        else {
            Write-Host "Deleting resource group '$ResourceGroupName'..." -ForegroundColor $ColorInfo
            Write-Host "This may take several minutes..." -ForegroundColor $ColorWarning
            
            $job = Start-Job -ScriptBlock {
                param($rgName, $subscriptionId)
                az account set --subscription $subscriptionId
                az group delete --name $rgName --yes --no-wait --output none
            } -ArgumentList $ResourceGroupName, $SubscriptionId
            
            # Show progress
            $dots = 0
            while ($job.State -eq "Running") {
                $dots = ($dots + 1) % 4
                $progress = "." * $dots + " " * (3 - $dots)
                Write-Host "`rDeleting resource group$progress" -NoNewline -ForegroundColor $ColorInfo
                Start-Sleep -Seconds 1
            }
            
            Write-Host "`n"
            $result = Receive-Job -Job $job
            Remove-Job -Job $job
            
            Write-CleanupResult "Resource Group Deletion" $true "Started deletion of $ResourceGroupName (async)"
            Write-Host "💡 The deletion will continue in the background. Check Azure Portal for status." -ForegroundColor $ColorInfo
        }
    }
    catch {
        Write-CleanupResult "Resource Group Deletion" $false "Error: $($_.Exception.Message)"
    }
}

function Show-CleanupSummary {
    Write-Host "`n" -NoNewline
    Write-Host "🎯 Cleanup Summary" -ForegroundColor $ColorInfo
    Write-Host "=================" -ForegroundColor $ColorInfo
    
    if ($WhatIf) {
        Write-Host "✅ What-If analysis completed successfully" -ForegroundColor $ColorSuccess
        Write-Host "💡 No actual resources were deleted" -ForegroundColor $ColorInfo
        Write-Host "📝 Review the output above to see what would be deleted" -ForegroundColor $ColorInfo
    }
    elseif ($SelectiveCleanup) {
        Write-Host "✅ Selective cleanup completed" -ForegroundColor $ColorSuccess
        Write-Host "💡 Some resources may still exist in the resource group" -ForegroundColor $ColorInfo
        Write-Host "🔍 Use Azure Portal to verify the current state" -ForegroundColor $ColorInfo
    }
    else {
        Write-Host "✅ Full cleanup initiated" -ForegroundColor $ColorSuccess
        Write-Host "⏳ Resource group deletion is running in the background" -ForegroundColor $ColorWarning
        Write-Host "🔍 Monitor progress in Azure Portal" -ForegroundColor $ColorInfo
        Write-Host "💰 Billing will stop once all resources are deleted" -ForegroundColor $ColorInfo
    }
    
    Write-Host "`n📋 Next Steps:" -ForegroundColor $ColorInfo
    Write-Host "1. Check Azure Portal to verify deletion status" -ForegroundColor White
    Write-Host "2. Monitor your Azure bill to ensure charges have stopped" -ForegroundColor White
    Write-Host "3. Remove any local configuration files if no longer needed" -ForegroundColor White
    
    if (-not $WhatIf) {
        Write-Host "`n⚠️  Important Notes:" -ForegroundColor $ColorWarning
        Write-Host "• Deleted resources cannot be recovered" -ForegroundColor White
        Write-Host "• Some resources may take time to fully delete" -ForegroundColor White
        Write-Host "• Backup any important data before cleanup" -ForegroundColor White
    }
}

# Main execution
try {
    Write-Host "🧹 ADF Monitor Pro Environment Cleanup" -ForegroundColor $ColorInfo
    Write-Host "=======================================" -ForegroundColor $ColorInfo
    Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor White
    Write-Host "Subscription: $SubscriptionId" -ForegroundColor White
    
    if ($WhatIf) {
        Write-Host "Mode: What-If Analysis (no actual changes)" -ForegroundColor $ColorInfo
    }
    elseif ($SelectiveCleanup) {
        Write-Host "Mode: Selective Cleanup" -ForegroundColor $ColorInfo
    }
    else {
        Write-Host "Mode: Complete Cleanup" -ForegroundColor $ColorError
    }
    
    # Step 1: Test Azure connection
    if (-not (Test-AzureConnection)) {
        exit 1
    }
    
    # Step 2: Get resource group info
    $rgInfo = Get-ResourceGroupInfo
    if (-not $rgInfo) {
        exit 1
    }
    
    # Step 3: Confirm deletion
    if (-not $WhatIf) {
        if (-not (Confirm-Deletion -Resources $rgInfo.Resources -ResourceGroupName $ResourceGroupName)) {
            Write-Host "❌ Cleanup cancelled by user" -ForegroundColor $ColorWarning
            exit 0
        }
    }
    
    # Step 4: Perform cleanup
    if ($SelectiveCleanup) {
        Remove-SelectiveResources -Resources $rgInfo.Resources
    }
    else {
        Remove-EntireResourceGroup
    }
    
    # Step 5: Show summary
    Show-CleanupSummary
    
    Write-Host "`n🎉 Cleanup process completed!" -ForegroundColor $ColorSuccess
}
catch {
    Write-Host "`n❌ Cleanup failed with error: $($_.Exception.Message)" -ForegroundColor $ColorError
    Write-Host "Error details:" -ForegroundColor $ColorError
    Write-Host $_.Exception.ToString() -ForegroundColor $ColorError
    exit 1
}