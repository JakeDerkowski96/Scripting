function Get-PurviewSensitivityLabels {
    <#
    .SYNOPSIS
        Lists Microsoft Purview sensitivity labels via the Microsoft Graph information protection API.

    .DESCRIPTION
        Authenticates with the OAuth 2.0 client-credentials flow and queries the Graph beta
        'security/informationProtection/sensitivityLabels' endpoint, returning the labels
        published in the tenant (name, priority, tooltip, and parent/child relationships).

        The app registration must be granted the 'InformationProtectionPolicy.Read.All'
        application permission (admin consent required).

        Note: this endpoint currently lives under the Graph beta profile.

    .PARAMETER ClientId
        Application (client) ID of the Entra app registration.

    .PARAMETER ClientSecret
        Client secret for the app registration.

    .PARAMETER TenantId
        Directory (tenant) ID.

    .EXAMPLE
        Get-PurviewSensitivityLabels -ClientId $id -ClientSecret $secret -TenantId $tenant |
            Sort-Object priority | Format-Table name, priority, isActive

    .LINK
        https://learn.microsoft.com/en-us/graph/api/security-informationprotection-list-sensitivitylabels
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ClientId,

        [Parameter(Mandatory)]
        [string]$ClientSecret,

        [Parameter(Mandatory)]
        [string]$TenantId
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
    $uri = "https://graph.microsoft.com/beta/security/informationProtection/sensitivityLabels"

    $labels = [System.Collections.Generic.List[object]]::new()
    do {
        $page = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
        foreach ($label in $page.value) { $labels.Add($label) }
        $uri = $page.'@odata.nextLink'
    } while ($uri)

    return $labels
}
