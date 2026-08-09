<# 
.SYNOPSIS
    Lists required permissions (RequiredResourceAccess) for all app registrations.

.EXAMPLE
    PS C:\> .\Get-AzureADPSRequiredPermissions.ps1 | Export-Csv -Path "required_permissions.csv" -NoTypeInformation
    Generates a CSV report of all required permissions declared by all apps.
#>

[CmdletBinding()]
param()

# Get tenant details to test that Connect-AzureAD has been called
try {
    $tenant_details = Get-AzureADTenantDetail
} catch {
    throw "You must call Connect-AzureAD before running this script."
}
Write-Verbose ("TenantId: {0}, InitialDomain: {1}" -f `
                $tenant_details.ObjectId, `
                ($tenant_details.VerifiedDomains | Where-Object { $_.Initial }).Name)

# An in-memory cache of ServicePrincipal objects by AppId
$script:ServicePrincipalByAppId = @{}
function GetServicePrincipalByAppId($AppId) {
    if (-not $script:ServicePrincipalByAppId.ContainsKey($AppId)) {
        Write-Verbose ("Querying Azure AD for ServicePrincipal with AppId '{0}'" -f $AppId)
        $object = Get-AzureADServicePrincipal -Filter ("appId eq '{0}'" -f $AppId)
        if ($object) {
            $script:ServicePrincipalByAppId[$object.AppId] = $object
        } else {
            Write-Warning ("ServicePrincipal for AppId '{0}' not found." -f $AppId)
        }
    }
    return $script:ServicePrincipalByAppId[$AppId]
}

# Iterate over all Application objects and get the RequiredResourceAccess
Write-Verbose "Retrieving Application objects..."
Get-AzureADApplication -All $true | ForEach-Object { $i = 0 } {
    $app = $_
    
    $app.RequiredResourceAccess | ForEach-Object {

        $requiredResourceAccess = $_
        $resource = GetServicePrincipalByAppId -AppId $requiredResourceAccess.ResourceAppId 
        $requiredResourceAccess.ResourceAccess | ForEach-Object {
            
            $resourceAccess = $_
            $permission = New-Object PSObject -Property ([ordered]@{
                "PermissionType" = ""
                "ResourceObjectId" = $resource.ObjectId
                "ResourceAppId" = $requiredResourceAccess.ResourceAppId
                "ResourceDisplayName" = $resource.DisplayName
                "Permission" = ""
            })

            if ($resourceAccess.Type -eq "Role") {
                $appRole = $resource.AppRoles | Where-Object { $_.Id -eq $resourceAccess.Id }
                $permission.PermissionType = "Application"
                $permission.Permission = $appRole.Value
            } elseif ($resourceAccess.Type -eq "Scope") {
                $oauth2Permission = $resource.OAuth2Permissions | Where-Object { $_.Id -eq $resourceAccess.Id }
                $permission.PermissionType = "Delegated"
                $permission.Permission = $oauth2Permission.Value
            }

            $permission
        }
    }
}