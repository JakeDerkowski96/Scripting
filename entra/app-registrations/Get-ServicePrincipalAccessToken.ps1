function Get-ServicePrincipalAccessToken {
    <#
    .SYNOPSIS
    Easily retrieve your Service Principal's access token
    .EXAMPLE
    $userToken = Get-UserAccessToken
    Write-Host "User Access Token: $userToken"
    #>

    # Authenticate using service principal credentials
    
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]$servicePrincipalAppId,

        [Parameter(Mandatory)]
        [string]$servicePrincipalSecret
    )

    Connect-AzAccount -ServicePrincipal -ApplicationId $servicePrincipalAppId -Credential (New-Object PSCredential -ArgumentList $servicePrincipalAppId, (ConvertTo-SecureString $servicePrincipalSecret -AsPlainText -Force))

    # Retrieve the access token
    $AccessToken = Get-AzAccessToken -ResourceUrl "https://graph.microsoft.com"

    # Return the access token
    return $AccessToken.Token
}