#Requires -Module Az.Resources

function New-AzureResourceGroup {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name,

        [Parameter(Mandatory)]
        [string]$Location
    )

    $context = Get-AzContext
    if (-not $context) {
        Write-Error "No active Azure context. Run Connect-AzAccount first."
        return
    }

    try {
        New-AzResourceGroup -Name $Name -Location $Location
        Write-Verbose "Created resource group: $Name in $Location"
    }
    catch {
        Write-Error "Failed to create resource group '$Name': $($_.Exception.Message)"
    }
}
