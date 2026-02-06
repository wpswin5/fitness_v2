param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$Location = "eastus",
    
    [string]$TemplateFile = "./bicep/main.bicep",
    [string]$ParametersFile = "./bicep/parameters.json"
)

# Ensure resource group exists
Write-Host "Creating/verifying resource group: $ResourceGroupName"
az group create --name $ResourceGroupName --location $Location

# Deploy Bicep template
Write-Host "Deploying Azure resources..."
az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file $TemplateFile `
    --parameters $ParametersFile

Write-Host "Deployment completed!"
