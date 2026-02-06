# Deployment Guide

## Prerequisites

- Azure CLI installed
- GitHub repository with secrets configured (see [SECRETS_SETUP.md](./SECRETS_SETUP.md))
- Azure subscription with appropriate permissions
- Bicep CLI (included with latest Azure CLI)

## Architecture Overview

```
GitHub Push
    ↓
CI Pipeline (test, lint)
    ↓
Build & Deploy DB Infrastructure (Bicep)
    ↓
Run DB Migrations (SQL)
    ↓
Build Docker Image
    ↓
Push to ACR
    ↓
Deploy to Azure Container Instances/App Service
```

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd fitness_v2
```

### 2. Set Up Python Environment
```bash
cd app
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp ../.env.example .env
# Edit .env with your local development values
```

### 4. Run Locally
```bash
python -m uvicorn main:app --reload
# API will be available at http://localhost:8000
```

### 5. Run Tests
```bash
pytest tests/ -v
```

## Deployment to Azure

### Development Environment
1. Merge to `develop` branch
2. GitHub Actions CI runs automatically
3. Manual approval gates (if configured)
4. Deploys to dev resources

### Production Environment
1. Merge to `main` branch
2. GitHub Actions runs full pipeline
3. Deploys to prod resources
4. Can also trigger manually via `workflow_dispatch`

### Manual Deployment

If you need to deploy manually:

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription {subscription-id}

# Deploy database infrastructure
cd database/scripts
./deploy-infrastructure.ps1 -ResourceGroupName {resource-group} -Location eastus

# Run migrations
./deploy-db.ps1 \
  -ServerName {sql-server-name} \
  -DatabaseName {database-name} \
  -UserId {admin-user} \
  -Password {admin-password}

# Build and push Docker image
cd ../../app
az acr build \
  --registry {registry-name} \
  --image fitness-api:latest \
  --file Dockerfile .

# Deploy container
az container create \
  --resource-group {resource-group} \
  --name fitness-api-dev \
  --image {registry}.azurecr.io/fitness-api:latest \
  --port 8000 \
  --environment-variables \
    DB_SERVER={server} \
    DB_NAME={db-name} \
    DB_USER={user} \
    DB_PASSWORD={password}
```

## Monitoring Deployments

### GitHub Actions
- View workflow runs in repository Settings → Actions
- Check workflow logs for errors
- Review test coverage reports

### Azure Resources
```bash
# Check container status
az container show \
  --resource-group {resource-group} \
  --name fitness-api-dev \
  --query "containers[0].instanceView.currentState"

# View logs
az container logs \
  --resource-group {resource-group} \
  --name fitness-api-dev

# Check database
az sql db show \
  --resource-group {resource-group} \
  --server {server-name} \
  --name {database-name}
```

## Rollback Procedures

### Database
1. Identify failing migration version
2. Create rollback migration script
3. Apply rollback via GitHub Actions or manual deployment

### Application
```bash
# Redeploy previous image version
az container create \
  --resource-group {resource-group} \
  --name fitness-api-dev \
  --image {registry}.azurecr.io/fitness-api:{previous-tag}
```

## Troubleshooting

### Database Connection Issues
- Verify firewall rules allow Azure services
- Check connection string format in environment variables
- Ensure ODBC drivers are installed (done in Dockerfile)

### Deployment Failures
- Check GitHub Actions logs for specific error messages
- Verify Azure credentials are valid
- Ensure service principal has correct permissions
- Check Docker image builds successfully locally

### Performance
- Review database query performance
- Monitor container CPU/memory usage
- Check Azure SQL Database DTU consumption
