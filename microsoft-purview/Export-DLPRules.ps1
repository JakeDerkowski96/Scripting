[Parameter(Mandatory)][string]$OutputDirectory

Import-Module ExchangeOnlineManagement
Connect-IPPSSession -UserPrincipalName $superuser

$OutputDirectory = "dir"
$OutputFile = "file"
$OutputPath = "$OutputDirectory\$OutputFile"
$Rules = (Get-DlpComplianceRule | Out-GridView -Title "Select the rules you wish to export" -PassThru)
foreach($rule in $rules){
    $tempName = $rule.Name -replace '\s+', ''
    $fileName = "${tempName}.json"
    $OutPath = "$OutputDirectory\$fileName"

    $rule | Add-Member -NotePropertyName "Policy" -NotePropertyValue $rule.ParentPolicyName
    $rule.PSObject.Properties.Remove('ParentPolicyName')

    $rule | ConvertTo-Json -Depth 100 | Out-File -FilePath $OutPath -Encoding UTF8

}
