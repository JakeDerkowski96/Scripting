# Deploy-ArmTemplateFolder.ps1

Param(
    $inFolder = "",
    $WorkspaceParameterFile = ""
)

$Tenant = @{
    Tenant         = "Tenantsec.com"
    TenantId       = ""
    Workspace      = "law-siem01"
    WorkspaceId    = ""
    ResourceGroup  = "rg-logs"
    Subscription   = "Tenant Trial Subscription"
    SubscriptionId = ""
    ResourceId     = "Sentinel ResourceId"
}

Connect-AzAccount -TenantId $Tenant.TenantId

$Templates = Get-ChildItem -Path $inFolder

foreach($template in $Templates){
    $deploymentName = "$($template.BaseName)_$($Tenant.Tenant)_$(Get-Random 1111)"

    if($deploymentName.Length -gt 83){
        $deploymentName = $deploymentName[0..64]
    }

    try {
        $deploymentInstance = New-AzResourceGroupDeployment `
        -Name $deploymentName `
        -TemplateFile $template `
        -ResourceGroupName $Tenant.ResourceGroup `
        -TemplateParameterFile $WorkspaceParameterFile

        Write-Host -ForegroundColor Green "$($deploymentName) was successful!"
        
    }
    catch {
        Write-Host -ForegroundColorRed "Deployment: $($deploymentName) failed"
    }





}