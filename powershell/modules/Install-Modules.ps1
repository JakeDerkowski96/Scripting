$ModulesToInstall = @(
    "Az.Accounts",
    "Az.Resources",
    "Az.OperationalInsights",
    "Az.SecurityInsights",
    "ExchangeOnlineManagement"
)

$InstalledModules = (Get-InstalledModule).Name


foreach ($module in $ModulesToInstall) {
    if (!($module -in $InstalledModules)) {
        Write-Verbose -Message "$module has not been installed"
        try {
            Install-Module -Name $module
            Write-Host -ForegroundColor Green "$module installed successfully!"            
        }
        catch {
            Write-Host -ForegroundColor Red "Installation failed for $module"
        }

    }
    else {
        Write-Verbose -Message "$module is already installed"
    }
}