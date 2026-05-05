#Requires -Module Az.Accounts

function Get-UserAccessToken {
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$ResourceUrl = "https://graph.microsoft.com"
    )

    $context = Get-AzContext
    if (-not $context) {
        Write-Error "No active Azure context. Run Connect-AzAccount first."
        return
    }

    $token = Get-AzAccessToken -ResourceUrl $ResourceUrl
    return $token.Token
}
