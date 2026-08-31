
<# 
.SYNOPSIS
    Grants (or removes) application permissions (app role assignments) to a client application.

.PARAMETER ClientId
    The AppId or one of the ServicePrincipalNames of the client service principal.

.PARAMETER Permissions
    A hashtable where the key is an identifier for the resource (either the AppId or one of the 
    ServicePrincipalNames) and the value is the space-separated list of app roles desired.

.PARAMETER RemoveAll
    Instead of adding permissions, this removes *all* application permissions granted to the client. 

.EXAMPLE
    PS C:\> .\Manage-AzureADPSAppRoleAssignments.ps1 -ClientId "2e5e4fad-5332-43fc-9293-6a349df34883" -Permissions @{"https://graph.microsoft.com" = "Directory.Read.All Sites.ReadWrite.All"}
    Grants application permissions Microsoft Graph API. 

.EXAMPLE
    PS C:\> .\Manage-AzureADPSAppRoleAssignments.ps1 -ClientId $client_id -RemoveAll
    Removes all application permissions previously granted to a client
#>

param(
    [Parameter(Mandatory = $true)]
    [string] $ClientId,
    [Hashtable] $Permissions,    
    [switch] $RemoveAll
)

# Parameter validation
if ((-not ($Permissions -or $RemoveAll)) -or ($Permissions -and $RemoveAll)) {
    throw "Either -Permissions or -RemoveAllPermissions must be passed, but not both."
}

# Get tenant details to test that Connect-AzureAD has been called
try {
    $tenant_details = Get-AzureADTenantDetail
} catch {
    throw "You must call Connect-AzureAD before running this script."
}
Write-Verbose ("TenantId: {0}, InitialDomain: {1}" -f `
                $tenant_details.ObjectId, `
                ($tenant_details.VerifiedDomains | Where-Object { $_.Initial }).Name)

# Get the client ServicePrincipal object
$client_filter = "servicePrincipalNames/any(c:c eq '{0}')" -f $ClientId
$client = Get-AzureADServicePrincipal -Filter $client_filter
if ($client.Count -lt 1) {
    throw ("ServicePrincipal not found for client '{0}'" -f $ClientId)
} elseif ($client.Count -gt 1) {
    throw ("Multiple ServicePrincipal ojects found for client '{0}'" -f $ClientId)    
}

# Get all existing app role assignments for the client
$existingAppRoleAssignments = Get-AzureADServiceAppRoleAssignedTo -ObjectId $client.ObjectId

if (-not $RemoveAll) {

    # Ensure an app role assignment exists for each desired permission
    $permissions.Keys | ForEach-Object {

        $resource_id = $_
        $scopes = $permissions[$_]

        # Get the resource ServicePrincipal object and exisitng app role assignments to it
        $resourceFilter = "servicePrincipalNames/any(c:c eq '{0}')" -f $resource_id
        $resource = Get-AzureADServicePrincipal -Filter $resourceFilter
        $existingPermissions = $existingAppRoleAssignments `
            | Where-Object { $_.ResourceId -eq $resource.ObjectId } `
            | Select-Object -ExpandProperty Id

        if ($resource.Count -eq 1) {

            $scopes.Split(" ") | ForEach-Object {

                $scope = $_
                
                # Find the matching AppRole on the resource ServicePrincipal object
                $appRole = $resource.AppRoles `
                    | Where-Object { $_.AllowedMemberTypes -contains "Application" } `
                    | Where-Object { $_.Value -eq $scope }   
            
                if ($appRole) {

                    if ($existingPermissions -and $existingPermissions -contains $appRole.Id) {
            
                        # Don't try to add an app role assignment that already exists.
                        Write-Output ("Permission '{0}' for '{1}' already exists. Skipping." -f `
                                        $appRole.Value, $resource.DisplayName)
                    } else {
                        
                        Write-Output ("Granting permission '{0}' for '{1}'..." -f `
                                        $appRole.Value, $resource.DisplayName)
            
                        $appRoleAssignment = New-AzureADServiceAppRoleAssignment `
                                                -ObjectId $client.ObjectId `
                                                -PrincipalId $client.ObjectId `
                                                -ResourceId $resource.ObjectId `
                                                -Id $appRole.Id
                    }
                } else {
            
                    Write-Warning ("AppRole with value '{0}' not found for resource '{1}'" -f `
                                    $scope, $resource.DisplayName)
                }
            }
        } elseif ($resource.Count -gt 1) {

            # AppId and ServicePrincipalNames should be unique, so this would be unexpected.
            Write-Error ("More than one ServicePrincipal found for resource '{0}'" -f $resource_id)
        } else {

            # AppId and ServicePrincipalNames should be unique, so this would be unexpected.
            Write-Error ("ServicePrincipal object not found for resource '{0}'" -f $resource_id)
        }
    }
} else {
    
    # Remove *all* of the client's app role assignments
    $existingAppRoleAssignments | ForEach-Object {

        Write-Output ("Removing permission '{0}' for '{1}'..." -f $_.Id, $resource.DisplayName)
        Remove-AzureADServiceAppRoleAssignment -ObjectId $client.ObjectId `
                                               -AppRoleAssignmentId $_.ObjectId
    }
}