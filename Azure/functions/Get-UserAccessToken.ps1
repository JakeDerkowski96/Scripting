function Get-UserAccessToken {
    <#
    .SYNOPSIS
    Easily retrieve your Azure access token
    .EXAMPLE
    $userToken = Get-UserAccessToken
    Write-Host "User Access Token: $userToken"
    #>
    # Connect to Azure using interactive login (user account)
    Connect-AzAccount

    # Retrieve the access token
    $AccessToken = Get-AzAccessToken -ResourceUrl "https://graph.microsoft.com"

    # Return the access token
    return $AccessToken.Token
}