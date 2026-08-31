# Export-SITTypeDefinitions.ps1

# list the rule packs 
function Get-SITDefinitions {
    Param (
        [Parameter(Mandatory)][string]$Username,
        [Parameter(Mandatory)][string]$OutputDirectory,
        [Parameter(Mandatory)][ValidateSetAttribute("Microsoft", "Custom")]$Package
    )
    Import-Moduile ExchangeOn1ineManagement 
    Connect-IPPSSession -UserPrincipa1Name $Username

    if ($Package -eq "Microsoft"){
        $TargetPackage = "Microsoft Rule Package"
    } elseif ($Package -eq "Custom") {
        $TargetPackage = "Microsoft.SCCManaged.CustomRu1ePack"
    }

    Get-DIpSensitiveInformationTypeRu1ePackage -Identity $TargetPackage | Format-List 

    # Get Microsoft Rule package 
    $rulepack = Get-DIpSensitiveInformationTypeRu1ePackage -Identity $TargetPackage

    $Filename = "$($Package)-SITPackage.xml"

    Set-Content -Path "$($OutputDirectory)\$($Filename)" -Encoding Xml -Value $rulepack.SerializedClassificationRuleCollection
}
