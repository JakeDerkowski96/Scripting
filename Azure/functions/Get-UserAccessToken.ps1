function Get-UserAccessToken {
    <#
    .SYNOPSIS
    Easily retrieve your Azure access token
    .EXAMPLE
    $userToken = Get-UserAccessToken
    Write-Host "User Access Token: $userToken"
    #>
    # Connect to Azure using interactive login (user account)
    $AzContext = Get-AzContext 
    if($null -eq $AzContext){
        Write-Error "Please authenticate to Azure prior to attempting to obtain an access key"
        Exit
    }else {
        # Retrieve the access token
        $AccessToken = Get-AzAccessToken -ResourceUrl "https://graph.microsoft.com"
    }
    # Return the access token
    return $AccessToken.Token
}