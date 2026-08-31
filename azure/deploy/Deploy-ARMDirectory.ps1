# requires Az.Accounts
<# 
.Description
This script will get all of the ARM templates in the path given via parameter and deploy them to the desired location
.Notes
Be aware of the required parameters per template! This is intended to be used on a directory containing ARM templates of a certain type of resource or resources that share thier required parameters
.Parameter templateDirectory
this is the path to the directory containing all of the ARM template you wish to deploy
#>

# Deploy-ArmTemplateFolder.ps1

Param(
    [Parameter(Mandatory)]
    [string]
    $templateDirectory,
    
    [Parameter(Mandatory)]
    [string]
    $ParameterFile
)



Connect-AzAccount

$AzContext = Get-AzContext

$targetSub = Get-AzSubscription | Out-Gridview -Title "Select your subscription you wish to deploy to" -PassThru
# $targetSub.Id

Set-AzContext -SubscriptionId $targetSub.Id

$targetRg = Get-AzResourceGroup | Select-Object ResourceGroupName, Location, Tags, ResourceId | Sort-Object -Property ResourceGroupName | Out-Gridview -Title "Select the target resource group to deploy in" -PassThru
# $targetRg.ResourceGroupName

$Templates = Get-ChildItem -Path $templateDirectory -Filter *.json -Recurse 

$deploySuccess = @()
$deployFailures = @()

foreach($template in $Templates){

    $templateInfo = Get-Item -Path $template

    $deploymentName = "$($templateInfo.BaseName)_$(Get-Random 1111)"

    # ensure name is not too long
    if($deploymentName.Length -gt 83){
        $deploymentName = $deploymentName[0..64]
    }

    # try {
        New-AzResourceGroupDeployment `
        -Name $deploymentName `
        -TemplateFile $templateInfo.FullName `
        -ResourceGroupName $targetRg.ResourceGroupName `
        -TemplateParameterFile $ParameterFile `
        -Verbose

        Write-Host -ForegroundColor Green "$($deploymentName) was successful!"
        $deploySuccess += $deploymentName
        
    # }
    # catch {
    #     Write-Host -ForegroundColor Red "Deployment: $($deploymentName) failed"
    #     $deployFailures += $template.BaseName
    # }
}
Write-Host -ForegroundColor Yellow "Process has completed."
Start-Sleep 1

Write-Host -ForegroundColor Cyan "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
Write-Host -ForegroundColor Cyan "`t`tDeployment Report"
Write-Host -ForegroundColor Cyan "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
Start-Sleep .5
Write-Host -ForegroundColor Green "`tSuccessful Deployments"
$deploySuccess | ForEach-Object { Write-Host -ForegroundColor Green $_ }
Write-Host -ForegroundColor Green "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
Start-Sleep .5

Write-Host -ForegroundColor Red "`tFailed Deployments"
$deployFailures | ForEach-Object { Write-Host -ForegroundColor Red $_ }
Write-Host -ForegroundColor Green "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
Start-Sleep .5