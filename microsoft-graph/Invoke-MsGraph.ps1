function Invoke-MsGraphApi {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ClientId,

        [Parameter(Mandatory)]
        [string]$ClientSecret,

        [Parameter(Mandatory)]
        [string]$TenantId,

        [Parameter(Mandatory)]
        [string]$ApiEndpoint,

        [Parameter()]
        [ValidateSet("Get", "Post", "Patch", "Delete")]
        [string]$Method = "Get",

        [Parameter()]
        [string]$Body
    )

    $tokenResponse = Invoke-RestMethod -Method Post `
        -Uri "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token" `
        -ContentType "application/x-www-form-urlencoded" `
        -Body @{
            client_id     = $ClientId
            scope         = "https://graph.microsoft.com/.default"
            client_secret = $ClientSecret
            grant_type    = "client_credentials"
        }

    $params = @{
        Method  = $Method
        Uri     = $ApiEndpoint
        Headers = @{ Authorization = "Bearer $($tokenResponse.access_token)" }
    }

    if ($Body) {
        $params['Body'] = $Body
        $params['ContentType'] = "application/json"
    }

    Invoke-RestMethod @params
}
