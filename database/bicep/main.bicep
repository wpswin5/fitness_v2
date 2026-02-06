param environment string = 'dev'
param location string = 'eastus2'
param adminPassword string

var uniqueSuffix = uniqueString(resourceGroup().id)
var environmentConfig = {
  dev: {
    skuName: 'B_Gen5_1'
    skuCapacity: 1
    storageSizeGB: 5
    backupRetentionDays: 7
  }
  prod: {
    skuName: 'P_2'
    skuCapacity: 2
    storageSizeGB: 128
    backupRetentionDays: 35
  }
}

var config = environmentConfig[environment]

resource sqlServer 'Microsoft.Sql/servers@2021-08-01-preview' = {
  name: 'sqlsrv-fitness-${environment}-${uniqueSuffix}'
  location: location
  properties: {
    administratorLogin: 'sqladmin'
    administratorLoginPassword: adminPassword
    version: '12.0'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2021-08-01-preview' = {
  parent: sqlServer
  name: 'fitnessdb-${environment}'
  location: location
  sku: {
    name: config.skuName
    capacity: config.skuCapacity
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: config.storageSizeGB * 1024 * 1024 * 1024
  }
}

resource firewall 'Microsoft.Sql/servers/firewallRules@2021-08-01-preview' = {
  parent: sqlServer
  name: 'AllowAllAzureIPs'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

output sqlServerName string = sqlServer.name
output sqlDatabaseName string = sqlDatabase.name
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
