# Confirm-ModuleVersion
function Confirm-ModuleVersion {
    <#
    .DESCRIPTION
    Depends on Write-LogFile function
    #>
    Param(
        [Parameter(Mandatory)][string]$moduleName
    )
    
    $currentVersionString = $version

    $currentVersion = [Version]$currentVersionString
    $latestVersionString = (Find-Module -Name $moduleName).Version.ToString()
    $latestVersion = [Version]$latestVersionString


    $latestVersion = (Find-Module -Name $moduleName).Version.ToString()

    if ($currentVersion -lt $latestVersion) {
        write-LogFile -Message "`n[INFO] You are running an outdated version ($currentVersion) of $moduleName. The latest version is ($latestVersion), please update to the latest version." -Color "Yellow"
    }
}