#Requires -Module Az.Resources
#Requires -Module Az.OperationalInsights

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory)]
    [string]$WorkspaceName,

    [Parameter(Mandatory)]
    [string]$Location
)

function Import-RequiredModule {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ModuleName
    )

    if (-not (Get-Module -Name $ModuleName -ListAvailable)) {
        Install-Module -Name $ModuleName -Scope CurrentUser -Repository PSGallery -Force
    }
    Import-Module $ModuleName -Force
}

Import-RequiredModule -ModuleName "Az"

Connect-AzAccount

Write-Host "Creating resource group..." -ForegroundColor Yellow
New-AzResourceGroup -Name $ResourceGroupName -Location $Location

Write-Host "Creating Log Analytics workspace..." -ForegroundColor Yellow
$workspace = New-AzOperationalInsightsWorkspace `
    -ResourceGroupName $ResourceGroupName `
    -Name $WorkspaceName `
    -Location $Location `
    -Sku Standard

Write-Host "Enabling Microsoft Sentinel..." -ForegroundColor Yellow
Set-AzOperationalInsightsIntelligencePack `
    -ResourceGroupName $ResourceGroupName `
    -WorkspaceName $WorkspaceName `
    -IntelligencePackName "AzureSecurityCenter" `
    -Enabled $true

Write-Host "Verifying Sentinel is enabled..." -ForegroundColor Yellow
Get-AzOperationalInsightsIntelligencePack `
    -ResourceGroupName $ResourceGroupName `
    -WorkspaceName $WorkspaceName |
    Where-Object { $_.Name -eq "AzureSecurityCenter" }

Write-Host "Creating sample analytic rule..." -ForegroundColor Yellow
$ruleQuery = @"
SecurityEvent
| where TimeGenerated > ago(1d)
| where EventID == 4625
"@

New-AzOperationalInsightsSavedSearch `
    -ResourceGroupName $ResourceGroupName `
    -WorkspaceName $WorkspaceName `
    -Name "SampleRule" `
    -DisplayName "Sample Rule for Failed Logins" `
    -Category "Security" `
    -Query $ruleQuery `
    -Version 1 `
    -Enabled $true

Write-Host "Deploying Azure Activity data connector..." -ForegroundColor Yellow
$subscriptionId = (Get-AzContext).Subscription.Id
$connectorId = "/subscriptions/$subscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$WorkspaceName/providers/Microsoft.SecurityInsights/dataConnectors/AzureActivity"

New-AzResource -ResourceId $connectorId -Properties @{}

Write-Host "Deployment complete." -ForegroundColor Green
