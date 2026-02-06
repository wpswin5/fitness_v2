# Secrets & Security Setup Guide

## Required GitHub Secrets

### Azure Authentication
```
AZURE_CREDENTIALS          - Service Principal credentials (JSON format)
AZURE_SUBSCRIPTION_ID      - Azure subscription ID
AZURE_RESOURCE_GROUP       - Azure resource group name
AZURE_REGISTRY_NAME        - Azure Container Registry name
AZURE_REGISTRY_LOGIN_SERVER - ACR login server (e.g., myregistry.azurecr.io)
AZURE_REGISTRY_USERNAME    - ACR username
AZURE_REGISTRY_PASSWORD    - ACR password
```

### Database
```
DB_SERVER                  - SQL Server FQDN
DB_NAME                    - Database name
DB_USER                    - Database admin username
DB_ADMIN_PASSWORD          - Database admin password Password1
```

## Setting Up Azure Service Principal

### 1. Create Service Principal
```bash
az ad sp create-for-rbac \
  --name "fitness-api-sp" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group}
```

### 2. Copy JSON output as AZURE_CREDENTIALS secret

### 3. Grant ACR Push Permission
```bash
az role assignment create \
  --assignee {sp-app-id} \
  --role AcrPush \
  --scope /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.ContainerRegistry/registries/{registry-name}
```

## Setting Up Azure SQL Database Credentials

1. Deploy database infrastructure (see [DEPLOYMENT.md](./DEPLOYMENT.md))
2. Retrieve connection details:
   ```bash
   az sql server list --resource-group {resource-group} --query "[].fullyQualifiedDomainName"
   ```
3. Add DB credentials as GitHub Secrets

## Local Development

1. Copy `.env.example` to `.env`
2. Fill in local development values
3. **Never commit `.env` file**

## Rotating Secrets

- Service Principal: Recreate and update AZURE_CREDENTIALS
- Database: Change password in Azure Portal and update GitHub Secret
- ACR: Regenerate access keys in Azure Portal
