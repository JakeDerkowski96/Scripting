function Get-AzResourceId {
    param (
        [Parameter(Mandatory = $true)][string]$ResourceName,
        [Parameter(Mandatory = $true)][string]$ResourceType
    )
    Write-Verbose -Message "A Azure connection is required to access resources"

    Write-Verbose -Message "Searching for $($ResourceType) with the name $($ResourceName)"

    $ResourceId = (Get-AzResource -Name $ResourceName -ResourceType $ResourceType).Identity.PrincipalId

    return $ResourceId   
}