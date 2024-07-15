function Invoke-MsGraphApi {
    param (
        [Parameter(Mandatory = $true)]
        [string]$ClientId,
        
        [Parameter(Mandatory = $true)]
        [string]$ClientSecret,
        
        [Parameter(Mandatory = $true)]
        [string]$TenantId,
        
        [Parameter(Mandatory = $true)]
        [string]$ApiEndpoint
    )

    # Obtain the OAuth 2.0 token
    $tokenResponse = Invoke-RestMethod -Method Post -Uri "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token" -ContentType "application/x-www-form-urlencoded" -Body @{
        client_id     = $ClientId
        scope         = "https://graph.microsoft.com/.default"
        client_secret = $ClientSecret
        grant_type    = "client_credentials"
    }

    $accessToken = $tokenResponse.access_token

    # Make the API call
    $apiResponse = Invoke-RestMethod -Method Get -Uri $ApiEndpoint -Headers @{
        Authorization = "Bearer $accessToken"
    }

    return $apiResponse
}