function Invoke-DefenderAdvancedHunting {
    <#
    .SYNOPSIS
        Runs a Microsoft Defender XDR advanced hunting (KQL) query via the Microsoft Graph security API.

    .DESCRIPTION
        Authenticates with the OAuth 2.0 client-credentials flow and posts a KQL query to
        the Graph 'runHuntingQuery' action. Returns the flattened result rows.

        The app registration must be granted the 'ThreatHunting.Read.All' application
        permission (admin consent required).

    .PARAMETER ClientId
        Application (client) ID of the Entra app registration.

    .PARAMETER ClientSecret
        Client secret for the app registration.

    .PARAMETER TenantId
        Directory (tenant) ID.

    .PARAMETER Query
        The KQL advanced hunting query to execute.

    .EXAMPLE
        Invoke-DefenderAdvancedHunting -ClientId $id -ClientSecret $secret -TenantId $tenant `
            -Query "DeviceProcessEvents | where Timestamp > ago(1h) | take 20"

    .LINK
        https://learn.microsoft.com/en-us/graph/api/security-security-runhuntingquery
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ClientId,

        [Parameter(Mandatory)]
        [string]$ClientSecret,

        [Parameter(Mandatory)]
        [string]$TenantId,

        [Parameter(Mandatory)]
        [string]$Query
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

    $response = Invoke-RestMethod -Method Post `
        -Uri "https://graph.microsoft.com/v1.0/security/runHuntingQuery" `
        -Headers @{ Authorization = "Bearer $($tokenResponse.access_token)" } `
        -ContentType "application/json" `
        -Body (@{ Query = $Query } | ConvertTo-Json)

    # 'results' is an array of objects whose properties are the query's output columns.
    return $response.results
}
