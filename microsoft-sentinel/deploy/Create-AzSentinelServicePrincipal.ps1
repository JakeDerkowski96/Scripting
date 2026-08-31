function Install-Module-If-Needed {
    param([string]$ModuleName)

    if (Get-Module -ListAvailable -Name $ModuleName) {
        Write-Host "Module '$($ModuleName)' already exists, continue..." -ForegroundColor Green
    }
    else {
        Write-Host "Module '$($ModuleName)' does not exist, installing..." -ForegroundColor Yellow
        Install-Module $ModuleName -Force -AllowClobber -ErrorAction Stop
        Write-Host "Module '$($ModuleName)' installed." -ForegroundColor Green
    }
}

function Connect-AzureADIfNotConnected {
    # Check if the Azure AD session is already established
    if (-not (Get-AzureADSignedInUser -ErrorAction SilentlyContinue)) {
        Write-Verbose "Not connected to Azure AD. Initiating connection..."
        
        # Attempt to connect interactively
        try {
            Connect-AzureAD -ErrorAction Stop
            Write-Verbose "Successfully connected to Azure AD."
        }
        catch {
            Write-Error "Failed to connect to Azure AD: $_"
            throw
        }
    }
    else {
        Write-Verbose "Already connected to Azure AD."
    }
}

$VerbosePreference = 'Continue'

# install dependancies
Install-Module-If-Needed -ModuleName "AzureAD"
Import-Module -Name AzureAD

# auth to entra
Connect-AzureADIfNotConnected -Verbose

# Create an Azure AD Application (Service Principal)
$applicationName = "Sentinel_Management"
$password = ConvertTo-SecureString -String "xpJnMq_w8HdPz-beaP" -AsPlainText -Force
$application = New-AzADApplication -DisplayName $applicationName 
New-AzADServicePrincipal -ApplicationId $application.ApplicationId

# Assign the Required Roles to the Service Principal
$roleDefinitionId = (Get-AzRoleDefinition -Name "Log Analytics Contributor").Id
New-AzRoleAssignment -RoleDefinitionId $roleDefinitionId -ServicePrincipalName $application.ApplicationId

# Assign Sentinel-Specific Roles
$sentinelRoleDefinitionId = (Get-AzRoleDefinition -Name "Microsoft Sentinel Contributor").Id
New-AzRoleAssignment -RoleDefinitionId $sentinelRoleDefinitionId -ServicePrincipalName $application.ApplicationId
