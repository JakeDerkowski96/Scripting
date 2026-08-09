param(
    [Parameter(Mandatory = $true)]
    $ResourceGroupName,
    $SubscriptionId,
    $PlaybookName,
    $OutputFilename
)


Import-Module LogicAppTemplate
Import-Module Az.Accounts


Login-AzAccount


function Get-LogicAppTemplate {
    [CmdletBinding()]
    Param (
        [Parameter(Mandatory=$true)] [string] $outfile 
    )
    $token = Get-AzAccessToken -ResourceUrl "https://management.azure.com" | Select-Object -ExpandProperty Token
        Get-LogicAppTemplate -LogicApp $PlaybookName -ResourceGroup $ResourceGroupName -SubscriptionId $SubscriptionId -Token $token -Verbose | Out-File $OutputFilename
}

Get-LogicAppTemplate outfile.json