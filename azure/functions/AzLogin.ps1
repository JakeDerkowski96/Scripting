#Requires -Module Az.Accounts

function Connect-AzureLogin {
    [CmdletBinding()]
    param()

    $RequiredModule = "Az.Accounts"

    if (-not (Get-Module -Name $RequiredModule)) {
        if (-not (Get-Module -ListAvailable -Name $RequiredModule)) {
            Write-Warning "Missing dependency: $RequiredModule. Attempting install..."
            try {
                Install-Module -Name $RequiredModule -Scope CurrentUser -Force
            }
            catch {
                Write-Error "Failed to install $RequiredModule: $($_.Exception.Message)"
                return
            }
        }
        Import-Module -Name $RequiredModule
    }

    Connect-AzAccount
}
