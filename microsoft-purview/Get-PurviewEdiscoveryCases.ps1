function Get-PurviewEdiscoveryCases {
    <#
    .SYNOPSIS
        Lists Microsoft Purview eDiscovery (Premium) cases via the Microsoft Graph security API.

    .DESCRIPTION
        Authenticates with the OAuth 2.0 client-credentials flow and queries the Graph
        'security/cases/ediscoveryCases' endpoint, following '@odata.nextLink' paging to
        return every case (display name, status, created/closed timestamps).

        The app registration must be granted the 'eDiscovery.Read.All' application
        permission (admin consent required).

    .PARAMETER ClientId
        Application (client) ID of the Entra app registration.

    .PARAMETER ClientSecret
        Client secret for the app registration.

    .PARAMETER TenantId
        Directory (tenant) ID.

    .PARAMETER Filter
        Optional OData $filter expression (e.g. "status eq 'active'").

    .EXAMPLE
        Get-PurviewEdiscoveryCases -ClientId $id -ClientSecret $secret -TenantId $tenant `
            -Filter "status eq 'active'" | Format-Table displayName, status, createdDateTime

    .LINK
        https://learn.microsoft.com/en-us/graph/api/security-casesroot-list-ediscoverycases
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
        [string]$Filter
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

    $uri = "https://graph.microsoft.com/v1.0/security/cases/ediscoveryCases"
    if ($Filter) {
        $uri += "?`$filter=" + [uri]::EscapeDataString($Filter)
    }

    $cases = [System.Collections.Generic.List[object]]::new()
    do {
        $page = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
        foreach ($case in $page.value) { $cases.Add($case) }
        $uri = $page.'@odata.nextLink'
    } while ($uri)

    return $cases
}
