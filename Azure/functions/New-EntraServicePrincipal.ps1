# New-EntraServicePrincipal.ps1
function New-EntraServicePrincipal{
    [CmdletBinding()]
    param (
        [Parameter()]
        [string]
        $Name,

        [Parameter()]
        [string]
        $Role,

        [Parameter()]
        [string]
        $Scope
    )

    $SP = New-AzADServicePrincipal -DisplayName $Name -Role $Role
    $SP
}

function AzSPAuth($tenantId, $appId, $appSecret){
    # Convert the application secret to a secure string
    $securePassword = ConvertTo-SecureString -String $appSecret -AsPlainText -Force
    $psCredential = New-Object System.Management.Automation.PSCredential ($appId, $securePassword)
    
    # Connect to Azure using the service principal credentials
    Connect-AzAccount -Credential $psCredential -TenantId $tenantId -ServicePrincipal
}


