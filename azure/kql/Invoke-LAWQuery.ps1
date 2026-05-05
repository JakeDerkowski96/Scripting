function Get-LAWAccessToken {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [guid]$TenantId,

        [Parameter(Mandatory)]
        [guid]$ClientId,

        [Parameter(Mandatory)]
        [string]$ClientSecret
    )

    $body = @{
        resource      = "https://management.core.windows.net/"
        client_id     = $ClientId
        grant_type    = "client_credentials"
        client_secret = $ClientSecret
    }

    $params = @{
        ContentType = "application/x-www-form-urlencoded"
        Headers     = @{ accept = "application/json" }
        Body        = $body
        Method      = "Post"
        Uri         = "https://login.windows.net/$TenantId/oauth2/token"
    }

    $token = Invoke-RestMethod @params
    return $token
}

function Invoke-LAWQuery {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [guid]$ClientId,

        [Parameter(Mandatory)]
        [string]$ClientSecret,

        [Parameter(Mandatory)]
        [guid]$TenantId,

        [Parameter(Mandatory)]
        [guid]$SubscriptionId,

        [Parameter(Mandatory)]
        [string]$ResourceGroup,

        [Parameter(Mandatory)]
        [string]$Workspace,

        [Parameter(Mandatory)]
        [string]$Query,

        [Parameter()]
        [string]$Timespan = "PT12H"
    )

    $token = Get-LAWAccessToken -TenantId $TenantId -ClientId $ClientId -ClientSecret $ClientSecret

    $uri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup/providers/Microsoft.OperationalInsights/workspaces/$Workspace/api/query?api-version=2017-01-01-preview"

    $json = @{ timespan = $Timespan; query = $Query } | ConvertTo-Json
    $body = [System.Text.Encoding]::UTF8.GetBytes($json)

    $params = @{
        Headers = @{
            "Content-Type"  = "application/json"
            "Authorization" = "Bearer $($token.access_token)"
            "Prefer"        = "response-v1=true"
        }
        Body   = $body
        Method = "Post"
        Uri    = $uri
    }

    try {
        $response = Invoke-WebRequest @params
        return $response.Content | ConvertFrom-Json
    }
    catch {
        Write-Error "KQL query failed: $($_.Exception.Message)"
    }
}
