// infra/main.bicep
param location string = 'eastus2'
param hubName string = 'hub-echocare'
param projectName string = 'proj-echocare'
param storageAccountName string = 'stechocare${uniqueString(resourceGroup().id)}'
param keyVaultName string = 'kvecho${uniqueString(resourceGroup().id)}'	

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false   // transcripts/prescriptions never public
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true          // accidental deletes are recoverable
    softDeleteRetentionInDays: 7
  }
}

resource hub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: hubName
  location: location
  kind: 'Hub'
  identity: { type: 'SystemAssigned' }
  properties: {
    friendlyName: 'EchoCare Hub'
    storageAccount: storage.id
    keyVault: keyVault.id
  }
}

resource project 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: projectName
  location: location
  kind: 'Project'
  identity: { type: 'SystemAssigned' }
  properties: {
    friendlyName: 'EchoCare Project'
    hubResourceId: hub.id
  }
}

output hubId string = hub.id
output projectId string = project.id
output storageAccountName string = storageAccountName
output keyVaultName string = keyVaultName