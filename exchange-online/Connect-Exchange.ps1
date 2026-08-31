Function Connect-Exchange {
    Param (
        [Parameter()][string]$ModuleName = "ExchangeOnlineManagement"
    )    
    Import-Module $ModuleName | Out-Null
    Write-Verbose -Message "Connecting to $($ModuleName) with currentuser"
    $user = "$($env:username)@$($USERDNSDOMAIN)"
    Connect-Exchange -UserPrincipalName $user | Out-Null
}