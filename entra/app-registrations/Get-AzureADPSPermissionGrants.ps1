<# 
.SYNOPSIS
    Lists delegated permission grants (OAuth2PermissionGrants) and application permissions grants (AppRoleAssignments) granted to an app.

.PARAMETER ObjectId
    The ObjectId of the ServicePrincipal object for the app in question.

.PARAMETER AppId
    The AppId of the ServicePrincipal object for the app in question.

.PARAMETER Preload
    Whether to preload user and service principals into cache. Useful for processing many apps in small or medium-sized tenants.

.EXAMPLE
    PS C:\> .\Get-AzureADPSPermissionGrants.ps1 -AppId "ec70084d-9b61-42bc-b29e-51e1ce39eb39"
    Gets all permissions granted to an app, identifying the app by AppId.

.EXAMPLE
    PS C:\> .\Get-AzureADPSPermissionGrants.ps1 -ObjectId "73523d04-f9e8-472c-b724-9cf68dcf81b7"
    Get all permission granted to an app, identifying the app by ObjectId.

.EXAMPLE
    PS C:\> Get-AzureADServicePrincipal -All $true | .\Get-AzureADPSPermissionGrants.ps1 -Preload
    Get all granted permissions for all apps in the organization.
#>

[CmdletBinding(DefaultParameterSetName = 'ByObjectId')]
param(

    [Parameter(ParameterSetName = 'ByObjectId', Mandatory = $true, ValueFromPipelineByPropertyName = $true)]
    $ObjectId,
    
    [Parameter(ParameterSetName = 'ByAppId', Mandatory = $true, ValueFromPipelineByPropertyName = $true)]
    $AppId,

    [switch] $Preload
)

begin {

    # Get tenant details to test that Connect-AzureAD has been called
    try {
        $tenant_details = Get-AzureADTenantDetail
    } catch {
        throw "You must call Connect-AzureAD before running this script."
    }
    Write-Verbose ("TenantId: {0}, InitialDomain: {1}" -f `
                    $tenant_details.ObjectId, `
                    ($tenant_details.VerifiedDomains | Where-Object { $_.Initial }).Name)

    # This bit of magic will let us get a fresh Microsoft Graph access token using the same sesion as the Azure AD PowerShell module
    $context = [Microsoft.Open.Azure.AD.CommonLibrary.AzureRmProfileProvider]::Instance.Profile.Context
    $showDialogType = [Microsoft.Open.Azure.AD.CommonLibrary.ShowDialog]
    $authenticationFactory = [Microsoft.Open.Azure.AD.CommonLibrary.AzureSession]::AuthenticationFactory
    $msGraphEndpointResourceId = "MsGraphEndpointResourceId"
    $msGraphEndpoint = $context.Environment.Endpoints[$msGraphEndpointResourceId]
    $auth = $authenticationFactory.Authenticate($context.Account, $context.Environment, $context.Tenant.Id.ToString(), $null, $showDialogType::Never, $null, $msGraphEndpointResourceId)

    # Build the headers used in manual Microsoft Graph requests, including the authorization header
    function GetHeaders {
        return @{
            # This returns the authorization header value with a fresh access token
            "Authorization" =  $script:auth.AuthorizeRequest($script:msGraphEndpointResourceId)
        }
    }

    # Make a GET request to Microsoft Graph and (optionally) page through the results
    function Get ($Query, [switch]$All) {
        do {
            $morePages = $false
            $result = Invoke-WebRequest -Method "Get" -Headers (GetHeaders) -Uri $Query
            if ($result -ne $null) {
                $r = $result.Content | ConvertFrom-Json
                if ("value" -in $r.PSObject.Properties.Name -and $r.value -is [array]) {
                    $r.value
                    if ($All -and $r.'@odata.nextLink') {
                        $Query = $r.'@odata.nextLink'
                        $morePages = $true
                    }
                } else {
                    $r
                }
            }
        } while ($morePages)
    }

    # Function to get appRoleAssignments from Microsoft Graph. We use Microsoft Graph because it avoids
    # having to sort out behavior differences in Get-AzureADServiceAppRoleAssignedTo and Get-AzureADServiceAppRoleAssignment
    function GetServicePrincipalAppRoleAssignments($PrincipalId) {
        Get -Query ("{0}/v1.0/servicePrincipals/{1}/appRoleAssignments" -f $script:msGraphEndpoint, $PrincipalId) -All
    }
    
    # An in-memory cache of objects by {object ID} and by {object class, object ID} 
    $script:ObjectByObjectId = @{}
    $script:ObjectByObjectClassId = @{}

    # Function to add an object to the cache
    function CacheObject($Object) {
        if ($Object) {
            if (-not $script:ObjectByObjectClassId.ContainsKey($Object.ObjectType)) {
                $script:ObjectByObjectClassId[$Object.ObjectType] = @{}
            }
            $script:ObjectByObjectClassId[$Object.ObjectType][$Object.ObjectId] = $Object
            $script:ObjectByObjectId[$Object.ObjectId] = $Object
        }
    }

    # Function to retrieve an object from the cache (if it's there), or from Azure AD (if not).
    function GetObjectByObjectId($ObjectId) {
        Write-Debug ("GetObjectByObjectId: ObjectId: '{0}'" -f $ObjectId)
        if (-not $script:ObjectByObjectId.ContainsKey($ObjectId)) {
            Write-Verbose ("Querying Azure AD for object '{0}'" -f $ObjectId)
            $object = Get-AzureADObjectByObjectId -ObjectId $ObjectId
            if ($object) {
                CacheObject -Object $object
            } else {
                throw ("Object not found for ObjectId: '{0}'" -f $ObjectId)
            }
        }
        return $script:ObjectByObjectId[$ObjectId]
    }

    $cache_preloaded = $false
    $behavior = $null
}

process {

    # Retrieve the client ServicePrincipal object (which also ensures it actually exists)
    if ($PSCmdlet.ParameterSetName -eq "ByObjectId") {
        try {
            $client = GetObjectByObjectId -ObjectId $ObjectId
        } catch {
            Write-Error ("Unable to retrieve client ServicePrincipal object by ObjectId: '{0}'" -f $ObjectId)
            throw $_
        }
    } elseif ($PSCmdlet.ParameterSetName -eq "ByAppId") {
        try {
            $client = Get-AzureADServicePrincipal -Filter ("appId eq '{0}'" -f $AppId)
            CacheObject -Object $client
        } catch {
            Write-Error ("Unable to retrieve client ServicePrincipal object by AppId: '{0}'" -f $AppId)
            throw $_
        }
    }

    Write-Verbose ("Client DisplayName: '{0}', ObjectId: '{1}, AppId: '{2}'" -f $client.DisplayName, $client.ObjectId, $client.AppId)

    # Get one page of User objects and one of ServicePrincipal objects, and add to the cache. For smaller tenants,
    # this avoids a large number of requests to get individual objects. This behavior can be skipped with -NoPreload,
    # in which the first time each object is needed it will be requested and loaded into the cache.
    if (($Preload) -and (-not $cache_preloaded)) {
        Write-Verbose ("Retrieving a page of User objects and a page of ServicePrincipal objects...")
        Get-AzureADServicePrincipal -Top 999 | ForEach-Object { CacheObject -Object $_ }
        Get-AzureADUser -Top 999 | ForEach-Object { CacheObject -Object $_ }
        $cache_preloaded = $true
    }

    # Get all delegated permission grants
    Write-Verbose "Retrieving delegated permission grants..."
    Get-AzureADServicePrincipalOAuth2PermissionGrant -ObjectId $client.ObjectId | ForEach-Object {
        $grant = $_
        if ($grant.Scope) {
            $grant.Scope.Split(" ") | Where-Object { $_ } | ForEach-Object {
                
                $scope = $_

                $resource = GetObjectByObjectId -ObjectId $grant.ResourceId
                $permission = $resource.OAuth2Permissions | Where-Object { $_.Value -eq $scope }

                $principalDisplayName = ""
                if ($grant.PrincipalId) {
                    $principal = GetObjectByObjectId -ObjectId $grant.PrincipalId
                    $principalDisplayName = $principal.DisplayName
                }

                return New-Object PSObject -Property ([ordered]@{
                    "PermissionType" = "Delegated"
                                    
                    "ClientObjectId" = $grant.ClientId
                    "ClientDisplayName" = $client.DisplayName
                    
                    "ResourceObjectId" = $grant.ResourceId
                    "ResourceDisplayName" = $resource.DisplayName

                    "Permission" = $scope
                    "PermissionId" = $permission.Id
                    "PermissionDisplayName" = $permission.AdminConsentDisplayName
                    "PermissionDescription" = $permission.AdminConsentDescription
                    
                    "ConsentType" = $grant.ConsentType
                    "PrincipalObjectId" = $grant.PrincipalId
                    "PrincipalDisplayName" = $principalDisplayName

                    "PermissionGrantId" = $grant.ObjectId
                })
            }
        }
    }

    # Get all application permission grants
    Write-Verbose "Retrieving app role assignments..."
    GetServicePrincipalAppRoleAssignments -PrincipalId $client.ObjectId | ForEach-Object {
        $assignment = $_

        $resource = GetObjectByObjectId -ObjectId $assignment.resourceId
        $appRole = $resource.AppRoles | Where-Object { $_.Id -eq $assignment.appRoleId }

        return New-Object PSObject -Property ([ordered]@{
            "PermissionType" = "Application"
            
            "ClientObjectId" = $assignment.principalId
            "ClientDisplayName" = $client.DisplayName
            
            "ResourceObjectId" = $assignment.resourceId
            "ResourceDisplayName" = $resource.DisplayName

            "Permission" = $appRole.Value
            "PermissionId" = $assignment.appRoleId
            "PermissionDisplayName" = $appRole.DisplayName
            "PermissionDescription" = $appRole.Description

            "PermissionGrantId" = $assignment.id
        })
    }
}
