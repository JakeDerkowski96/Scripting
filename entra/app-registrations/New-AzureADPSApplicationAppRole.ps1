<# 
.SYNOPSIS
    Adds a new AppRole to an Application.

.PARAMETER Application
    The Application object's object ID.

.PARAMETER AllowedMemberTypes
    The allowed member types, Application, User or both.

.PARAMETER DisplayName
    The app role's friendly display name.

.PARAMETER Description
    The app role's description.

.PARAMETER Value
    The app role's value, as it will be presented in the 'roles' claim.

.PARAMETER Disabled
    Whether the app role should be created in a disabled state.

.EXAMPLE
    PS C:\> Get-AzureADApplication -Filter "appId eq '859bb5ee-20c4-4c2c-b4d8-de870a3cf5d6'" | `
                .\New-AzureADPSApplicationAppRole.ps1 `
                    -AllowedMemberTypes "User" `
                    -DisplayName "My App Admin" `
                    -Description "Admin role for My App" `
                    -Value "admin"
    Creates a new user app role.

#>

[CmdletBinding()]
param(

    [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
    [Microsoft.Open.AzureAD.Model.Application] $Application,

    [Parameter(Mandatory = $true)]
    [string[]] $AllowedMemberTypes,

    [Parameter(Mandatory = $true)]
    [string] $DisplayName,

    [Parameter(Mandatory = $true)]
    [string] $Description,

    [Parameter(Mandatory = $true)]
    [string] $Value,

    [string] $Id = "",

    [switch] $Disabled
)

# Validate AllowedMemberTypes
$allowedAllowedMemberTypes = @("application", "user")
$AllowedMemberTypes | ForEach-Object { 
    if (-not $allowedAllowedMemberTypes.Contains($_.ToLower())) {
        throw "AllowedMemberTypes must be 'Application', 'User', or both."
    }
}

# Check for existing app role with same value
if ($Application.AppRoles.Where({ $_.Value -eq $Value })) {
    throw ("The AppRole value '{0}' already exists for this application." -f $Value)
}

# Check for existing OAuth2Permission with same value
$existingScope = $Application.OAuth2Permissions | Where-Object { $_.Value -eq $Value }
if ($existingScope) {
    if ($Id -eq $existingScope.Id) {
        Write-Verbose ("An existing OAuth2Permission was found for value '{0}' and Id '{1}'." -f $Value, $Id)
    } elseif ($Id -eq "") {
        $Id = $existingScope.Id
        Write-Verbose ("An existing OAuth2Permission was found for value '{0}', using '{1}' as Id." -f $Value, $Id)
    } else {
        throw ("An OAuth2Permission already exists with value '{0}', but different Id '{1}'." -f $Value, $existingScope.Id)
    }
}

if ($Id -eq "") {
    $Id = [Guid]::NewGuid().ToString()
}

# Create new AppRole object
$newAppRole = [Microsoft.Open.AzureAD.Model.AppRole]::new()
$newAppRole.DisplayName = $DisplayName
$newAppRole.Description = $Description
$newAppRole.Value = $Value
$newAppRole.Id = $Id
$newAppRole.IsEnabled = (-not $Disabled)
$newAppRole.AllowedMemberTypes = @($AllowedMemberTypes)

# Add new AppRole and apply changes to Application object
$appRoles = $Application.AppRoles
$appRoles += $newAppRole

$Application | Set-AzureADApplication -AppRoles $appRoles