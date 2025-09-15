@description('Environment name (prod, staging, dev)')
param environmentName string = 'dev'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Unique suffix for resource names')
param resourceSuffix string = uniqueString(resourceGroup().id)

@description('Admin email for notifications')
param adminEmail string

// Variables
var resourcePrefix = 'adf-monitor-${environmentName}'
var storageAccountName = 'adfmon${environmentName}${take(resourceSuffix, 6)}'
var keyVaultName = '${resourcePrefix}-kv-${take(resourceSuffix, 6)}'
var dataFactoryName = '${resourcePrefix}-df-${resourceSuffix}'
var logAnalyticsName = '${resourcePrefix}-la-${resourceSuffix}'
var appInsightsName = '${resourcePrefix}-ai-${resourceSuffix}'
var appServicePlanName = '${resourcePrefix}-asp-${resourceSuffix}'
var webAppName = '${resourcePrefix}-web-${resourceSuffix}'
var sqlServerName = '${resourcePrefix}-sql-${resourceSuffix}'
var sqlDatabaseName = 'TestDataWarehouse'

// Resource Group Tags
resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = {
  scope: subscription()
  name: resourceGroup().name
}

// Storage Account for Data Lake and ADF
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    isHnsEnabled: true // Data Lake Gen2
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
  tags: {
    Environment: environmentName
    Purpose: 'ADF-Monitor-Testing'
  }
}

// Storage Account Containers
resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource rawDataContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobServices
  name: 'raw-data'
  properties: {
    publicAccess: 'None'
  }
}

resource processedDataContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobServices
  name: 'processed-data'
  properties: {
    publicAccess: 'None'
  }
}

resource failedDataContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobServices
  name: 'failed-data'
  properties: {
    publicAccess: 'None'
  }
}

resource archiveDataContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobServices
  name: 'archive-data'
  properties: {
    publicAccess: 'None'
  }
}

// Key Vault for secrets
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenant().tenantId
    accessPolicies: []
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enablePurgeProtection: false
  }
  tags: {
    Environment: environmentName
    Purpose: 'ADF-Monitor-Testing'
  }
}

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
  tags: {
    Environment: environmentName
    Purpose: 'ADF-Monitor-Testing'
  }
}

// Application Insights
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    IngestionMode: 'LogAnalytics'
  }
  tags: {
    Environment: environmentName
    Purpose: 'ADF-Monitor-Testing'
  }
}

// SQL Server and Database for testing
resource sqlServer 'Microsoft.Sql/servers@2023-05-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: 'adfadmin'
    administratorLoginPassword: 'TempPassword123!'
    version: '12.0'
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
  }
  tags: {
    Environment: environmentName
    Purpose: 'ADF-Monitor-Testing'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-05-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
    capacity: 5
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: 2147483648
  }
  tags: {
    Environment: environmentName
    Purpose: 'ADF-Monitor-Testing'
  }
}

// SQL Firewall Rule to allow Azure services
resource sqlFirewallRule 'Microsoft.Sql/servers/firewallRules@2023-05-01-preview' = {
  parent: sqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Data Factory
resource dataFactory 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: dataFactoryName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
  }
  tags: {
    Environment: environmentName
    Purpose: 'ADF-Monitor-Testing'
  }
}

// Grant Data Factory access to Storage Account
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(storageAccount.id, dataFactory.id, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
    principalId: dataFactory.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Grant Data Factory access to Key Vault
resource keyVaultAccessPolicy 'Microsoft.KeyVault/vaults/accessPolicies@2023-07-01' = {
  parent: keyVault
  name: 'add'
  properties: {
    accessPolicies: [
      {
        tenantId: tenant().tenantId
        objectId: dataFactory.identity.principalId
        permissions: {
          secrets: ['get', 'list']
        }
      }
    ]
  }
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
    size: 'B1'
    family: 'B'
    capacity: 1
  }
  properties: {
    reserved: false
  }
  tags: {
    Environment: environmentName
    Purpose: 'ADF-Monitor-Testing'
  }
}

// Web App for ADF Monitor Pro
resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name: webAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      minTlsVersion: '1.2'
      ftpsState: 'FtpsOnly'
      appSettings: [
        {
          name: 'AZURE_SUBSCRIPTION_ID'
          value: subscription().subscriptionId
        }
        {
          name: 'AZURE_RESOURCE_GROUP'
          value: resourceGroup().name
        }
        {
          name: 'AZURE_DATA_FACTORY_NAME'
          value: dataFactoryName
        }
        {
          name: 'AZURE_KEY_VAULT_NAME'
          value: keyVaultName
        }
        {
          name: 'AZURE_STORAGE_ACCOUNT_NAME'
          value: storageAccountName
        }
        {
          name: 'AZURE_LOG_ANALYTICS_WORKSPACE_ID'
          value: logAnalytics.properties.customerId
        }
        {
          name: 'ENVIRONMENT_NAME'
          value: environmentName
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
      pythonVersion: '3.11'
    }
  }
  identity: {
    type: 'SystemAssigned'
  }
  tags: {
    Environment: environmentName
    Purpose: 'ADF-Monitor-Testing'
  }
}

// Grant Web App access to resources
resource webAppStorageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(storageAccount.id, webApp.id, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource webAppDataFactoryRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: dataFactory
  name: guid(dataFactory.id, webApp.id, '673868aa-7521-48a0-acc6-0f60742d39f5')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '673868aa-7521-48a0-acc6-0f60742d39f5') // Data Factory Contributor
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource webAppKeyVaultAccessPolicy 'Microsoft.KeyVault/vaults/accessPolicies@2023-07-01' = {
  parent: keyVault
  name: 'add'
  dependsOn: [keyVaultAccessPolicy]
  properties: {
    accessPolicies: [
      {
        tenantId: tenant().tenantId
        objectId: webApp.identity.principalId
        permissions: {
          secrets: ['get', 'list']
        }
      }
    ]
  }
}

// Store connection strings in Key Vault
resource storageConnectionStringSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'storage-connection-string'
  properties: {
    value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
  }
}

resource sqlConnectionStringSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'sql-connection-string'
  properties: {
    value: 'Server=tcp:${sqlServer.properties.fullyQualifiedDomainName},1433;Initial Catalog=${sqlDatabaseName};Persist Security Info=False;User ID=adfadmin;Password=TempPassword123!;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;'
  }
}

// Outputs
output resourceGroupName string = resourceGroup().name
output storageAccountName string = storageAccount.name
output keyVaultName string = keyVault.name
output dataFactoryName string = dataFactory.name
output webAppName string = webApp.name
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output logAnalyticsWorkspaceId string = logAnalytics.properties.customerId
output sqlServerName string = sqlServer.name
output sqlDatabaseName string = sqlDatabase.name
output environment string = environmentName
