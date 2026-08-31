# test this script
# loop in all Applications then every Application Loop this one to 
$sp = $sp = az ad app list --display-name "yourapplication"
$spIdList = ($sp |ConvertFrom-Json -AsHashtable).requiredResourceAccess.resourceAccess
# retreive the ID from Bucket
$RoleAppID = ($sp| ConvertFrom-Json ).requiredResourceAccess.resourceAppId
## receive all Roles and lookup inside
$appRolesArray = (az ad sp show --id $RoleAppID | ConvertFrom-Json -AsHashtable ).appRoles
 
$listRoles = @()
foreach ($itemSpId in $spIdList) {
    $itemSpId.id
     
    foreach($item in $appRolesArray ) {
        if ( $item.id -eq $itemSpId.id ){
            $listRoles += $item
            $item
        }
    }
}
$listRoles.count