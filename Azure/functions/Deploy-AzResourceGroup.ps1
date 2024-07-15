function Deploy-AzResourceGroup {
    <#
    .DESCRIPTION
    deploys a resource group
    .NOTES
    This function assume that there has already been a connection established to Azure
    #>
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)][string]$Name,

        [Parameter(Mandatory)][string]$Location
    )

    try {
        New-AzResourceGroup -Name $resourceGroupName -Location $location
        
    }
    catch {
        Write-Host -ForegroundColor Red "Failed to deploy resource group: $Name"
    }


}