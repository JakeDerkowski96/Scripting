# Get all Azure AD Applications, Permissions and Users using Powershell

Import-Module AzureAD
Connect-AzureAD

Get-AzureADServicePrincipal -All:$true |?{$_.Tags -eq "WindowsAzureActiveDirectoryIntegratedApp"}|
# for a limited output  use command below
# Select-Object ObjectId,AppDisplayName,AppId,PublisherName

# Get all Delegated Permissions granted to an application
#$ServicePrincipalId = (Get-AzureADServicePrincipal -Top 1).ObjectId
#Provide ObjectId of your service principal object
$ServicePrincipalId = "5614c8c4-22bb-45c7-9be3-47491152703d"
Get-AzureADServicePrincipalOAuth2PermissionGrant -ObjectId $ServicePrincipalId | FL


# Get all Application Permissions granted to an application
$AppPermissions = @()
$ResourceAppHash = @{}
#Provide ObjectId of your service principal object
$ServicePrincipalId = "5614c8c4-22bb-45c7-9be3-47491152703d"
$AppRoleAssignments = Get-AzureADServiceAppRoleAssignedTo -ObjectId $ServicePrincipalId
$AppRoleAssignments | ForEach-Object {
    $RoleAssignment = $_
    $AppRoles = {}
    If ($ResourceAppHash.ContainsKey($RoleAssignment.ResourceId)) {
        $AppRoles = $ResourceAppHash[$RoleAssignment.ResourceId]
    }
    Else {
        $AppRoles = (Get-AzureADServicePrincipal -ObjectId $RoleAssignment.ResourceId).AppRoles
        #Store AppRoles to re-use.
        #Probably all role assignments use the same resource (Ex: Microsoft Graph).
        $ResourceAppHash[$RoleAssignment.ResourceId] = $AppRoles
    }
    $AppliedRole = $AppRoles | Where-Object { $_.Id -eq $RoleAssignment.Id }  
    $AppPermissions += New-Object PSObject -property @{
        DisplayName  = $AppliedRole.DisplayName
        Roles        = $AppliedRole.Value
        Description  = $AppliedRole.Description
        IsEnabled    = $AppliedRole.IsEnabled
        ResourceName = $RoleAssignment.ResourceDisplayName
    }
}
$AppPermissions | FL


# Get users who are associated with the application
#Provide ObjectId of your service principal object
$ServicePrincipalId = "5614c8c4-22bb-45c7-9be3-47491152703d"
Get-AzureADServiceAppRoleAssignment -ObjectId $ServicePrincipalId | Select ResourceDisplayName, PrincipalDisplayName
