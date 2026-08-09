# Local deploys
param(
    [Parameter(Mandatory = $true)][string]$ResourceGroup,
    [Parameter(Mandatory = $true)][string]$ARMTemplatePath,
    [Parameter(Mandatory = $true)][string]$CustomParameters
)

# Deploy all of these playbooks without downloading or cloning this repository
$today = Get-Date -Format "MM-dd-yyyy"
$suffix = Get-Random -Maximum 100
$deploySuffix = $today + "_$suffix"
$DeploymentName = "ResourceName_" + $deploySuffix


New-AzResourceGroupDeployment `
    -Name $DeploymentName `
    -ResourceGroupName $ResourceGroup `
    -TemplateFile $ARMTemplatePath `
    -TemplateParameterFile $CustomParameters
