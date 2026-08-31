# Check resource group exists (Exception handling)
function ValidateRg {
    [CmdletBinding()]    
    param (
        [Parameter(Mandatory=$true)]
        [string]
        $resourceGroupName
    )
    Get-AzResourceGroup -Name $resourceGroupName -ErrorVariable notPresent -ErrorAction SilentlyContinue
    if ($notPresent){
        Write-Host "Resource Group $($resourceGroupName) was not found"
        Write-Host "Exiting..." -ForegroundColor Red
        break
    }
    else {
        return $resourceGroupName
    }
}

# --------------------------------------

# Get all resources from resource group
$resourceGroupName = $resourceGroup.ResourceGroupName
$resources = (Get-AzResource -resourceGroupName $resourceGroupName)
$resourcesId = $resources.ResourceId
