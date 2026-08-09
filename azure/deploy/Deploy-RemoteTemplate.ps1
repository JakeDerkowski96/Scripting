# Remote template deployments
param(
    [Parameter(Mandatory = $true)][string]$ResourceGroup,
    [Parameter(Mandatory = $true)][string]$RemoteUrl,
    [Parameter(Mandatory = $true)][string]$CustomParameters
    )

# Deploy all of these playbooks without downloading or cloning this repository
$today = Get-Date -Format "MM-dd-yyyy"
$suffix = Get-Random -Maximum 100
$deploySuffix = $today + "_$suffix"
$deploymentName = "ResourceName_" + $deploySuffix



New-AzResourceGroupDeployment -Name $deploymentName `
    -ResourceGroupName $ResourceGroup `
    -TemplateUri $RemoteUrl `
    -TemplateParameterFile $CustomParameters `
    -Verbose