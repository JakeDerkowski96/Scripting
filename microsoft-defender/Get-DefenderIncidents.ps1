function Get-DefenderIncidents {
    <#
    .SYNOPSIS
        Retrieves Microsoft Defender XDR incidents via the Microsoft Graph security API.

    .DESCRIPTION
        Authenticates with the OAuth 2.0 client-credentials flow and queries the Graph
        'security/incidents' endpoint. Supports OData filtering and transparently follows
        '@odata.nextLink' paging so the full result set is returned.

        The app registration must be granted the 'SecurityIncident.Read.All' application
        permission (admin consent required).

    .PARAMETER ClientId
        Application (client) ID of the Entra app registration.

    .PARAMETER ClientSecret
        Client secret for the app registration.

    .PARAMETER TenantId
        Directory (tenant) ID.

    .PARAMETER Filter
        Optional OData $filter expression (e.g. "status eq 'active'").

    .PARAMETER Top
        Page size passed as $top. Defaults to 50.

    .EXAMPLE
        Get-DefenderIncidents -ClientId $id -ClientSecret $secret -TenantId $tenant `
            -Filter "severity eq 'high' and status eq 'active'"

    .LINK
        https://learn.microsoft.com/en-us/graph/api/security-list-incidents
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ClientId,

        [Parameter(Mandatory)]
        [string]$ClientSecret,

        [Parameter(Mandatory)]
        [string]$TenantId,

        [Parameter()]
        [string]$Filter,

        [Parameter()]
        [ValidateRange(1, 1000)]
        [int]$Top = 50
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

    $headers = @{ Authorization = "Bearer $($tokenResponse.access_token)" }

    $uri = "https://graph.microsoft.com/v1.0/security/incidents?`$top=$Top"
    if ($Filter) {
        $uri += "&`$filter=" + [uri]::EscapeDataString($Filter)
    }

    $incidents = [System.Collections.Generic.List[object]]::new()
    do {
        $page = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
        foreach ($incident in $page.value) { $incidents.Add($incident) }
        $uri = $page.'@odata.nextLink'
    } while ($uri)

    return $incidents
}
