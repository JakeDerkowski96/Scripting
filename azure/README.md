# Azure

PowerShell functions for Azure resource management.

## functions/

| Script | Purpose |
|--------|---------|
| `AzLogin.ps1` | Authenticate to Azure with automatic module dependency management |
| `Deploy-ARMTemplate.ps1` | Deploy ARM templates to a resource group |
| `Get-UserAccessToken.ps1` | Retrieve an access token for Azure/Graph API calls |
| `New-AzResourceGroup.ps1` | Create a new Azure resource group |
| `New-EntraServicePrincipal.ps1` | Create Entra service principals and authenticate as one |

## kql/

| Script | Purpose |
|--------|---------|
| `Invoke-LAWQuery.ps1` | Execute KQL queries against a Log Analytics workspace via REST API |
