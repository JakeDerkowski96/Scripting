function AzLogin(){
    $RequiredModule = "Az.Accounts"
    $Modules = (Get-Module).Name
    if($RequiredModule -notin $Modules.Name){
        # module has not been imported
        $AvailableModules = (Get-Module -ListAvailable).Name
        if($RequiredModule -notin $AvailableModules){
            Write-Host -ForegroundColor Red "Missing dependancies: $RequiredModule"
            Start-Sleet 2
            Write-Host -ForegroundColor Yellow "Trying to install: $RequiredModule"
            try {
                Install-Module -Name $RequiredModule -Scope CurrentUser
                Import-Module -name $RequiredModule
            }
            catch {
                Write-Host -ForegroundColor Red $_.Exception.Message
                Exit
            }
        }else {
            # Module has been installed, just not yet imported
            Import-Module -Name $RequiredModule
        }
    }
    Connect-AzAccount
}