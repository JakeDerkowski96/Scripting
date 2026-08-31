param(
    [Parameter(Mandatory = $true)]$MIGuid
)

$MI = Get-AzureADServicePrincipal -ObjectId $MIGuid

$MDEAppId = "fc780465-2017-40d4-a0c5-307022471b92"
$PermissionName = "Machine.Isolate" 

$MDEServicePrincipal = Get-AzureADServicePrincipal -Filter "appId eq '$MDEAppId'"

$AppRole = $MDEServicePrincipal.AppRoles | Where-Object { $_.Value -eq $PermissionName -and $_.AllowedMemberTypes -contains "Application" }
New-AzureAdServiceAppRoleAssignment -ObjectId $MI.ObjectId -PrincipalId $MI.ObjectId `
    -ResourceId $MDEServicePrincipal.ObjectId -Id $AppRole.Id
###################################################################################################

$roleName = "Security Admin"

$role = Get-AzureADDirectoryRole | Where-Object { $_.displayName -eq $roleName }

if ($null -eq $role) {
    $roleTemplate = Get-AzureADDirectoryRoleTemplate | Where-Object { $_.displayName -eq $roleName }
    
    Enable-AzureADDirectoryRole -RoleTemplateId $roleTemplate.ObjectId
    $role = Get-AzureADDirectoryRole | Where-Object { $_.displayName -eq $roleName }
}

Add-AzureADDirectoryRoleMember -ObjectId $role.ObjectId -RefObjectId $MI.ObjectID

New-AzRoleAssignment -ObjectId $MIGuid `
    -RoleDefinitionName $roleName `
    -Scope /subscriptions/$SubscriptionId/resourcegroups/$ResourceGroup
    
###################################################################################################