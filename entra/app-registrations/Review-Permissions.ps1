Connect-AzureAD

# Get Service Principal using objectId
$sp = Get-AzureADServicePrincipal -ObjectId "<ServicePrincipal objectID>"

# Get all delegated permissions for the service principal
$spOAuth2PermissionsGrants = Get-AzureADOAuth2PermissionGrant -All $true| Where-Object { $_.clientId -eq $sp.ObjectId }

# Remove all delegated permissions
$spOAuth2PermissionsGrants | ForEach-Object {
    Remove-AzureADOAuth2PermissionGrant -ObjectId $_.ObjectId
}

# Get all application permissions for the service principal
$spApplicationPermissions = Get-AzureADServiceAppRoleAssignedTo -ObjectId $sp.ObjectId -All $true | Where-Object { $_.PrincipalType -eq "ServicePrincipal" }

# Remove all delegated permissions
$spApplicationPermissions | ForEach-Object {
    Remove-AzureADServiceAppRoleAssignment -ObjectId $_.PrincipalId -AppRoleAssignmentId $_.objectId
  #############################################################################
  
 $app = Get-AzureADApplication -ObjectId '<object-id of the App Registration>'
$app.requiredResourceAccess | ConvertTo-Json -Depth 3
}


https://stackoverflow.com/questions/60769329/retrieve-api-permissions-of-azure-ad-application-via-powershell#:~:text=Get%20the%20Application%20permissions%20which%20has%20been%20granted,not%20get%20the%20permission%20with%20the%20command%20above.
