#Requires -Module Az.Resources

function New-EntraServicePrincipal {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name,

        [Parameter(Mandatory)]
        [string]$Role,

        [Parameter()]
        [string]$Scope
    )

    $params = @{
        DisplayName = $Name
        Role        = $Role
    }

    if ($Scope) {
        $params['Scope'] = $Scope
    }

    New-AzADServicePrincipal @params
}

function Connect-AzServicePrincipal {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$TenantId,

        [Parameter(Mandatory)]
        [string]$AppId,

        [Parameter(Mandatory)]
        [string]$AppSecret
    )

    $securePassword = ConvertTo-SecureString -String $AppSecret -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential($AppId, $securePassword)

    Connect-AzAccount -Credential $credential -TenantId $TenantId -ServicePrincipal
}
