<#
.DESCRIPTION
This script builds a Sentinel instance from the group up, customization is made possible at every step
#>


[CmdletBinding()]
param (
    [Parameter(Mandatory)][string]$resourceGroupName,
    
    [Parameter(Mandatory)][string]$workspaceName,

    [Parameter(Mandatory)][string]$region
)

function Import-requiredModules{
    [CmdletBinding()]
    param (
        [Parameter()]
        [string]
        $moduleName
    )
    try {
        Import-Module $moduleName
        Write-Host -ForegroundColor Green "Successfully imported: $moduleName"
    }
    catch {
        Install-Module  -Name $moduleName -Scope CurrentUser -Repository PSGallery -Force
        Import-Module $moduleName -Force
    }    
}
Install-Module  -Name Az -Scope CurrentUser -Repository PSGallery -Force
Import-Module Az

# Authenticate to Azure (interactive login)
$AzSesh = Connect-AzAccount


# Create a Resource Group
Write-Host "Creating Resource Group..."
New-AzResourceGroup -Name $resourceGroupName -Location $location

# Create a Log Analytics Workspace
Write-Host "Creating Log Analytics Workspace..."
$workspace = New-AzOperationalInsightsWorkspace -ResourceGroupName $resourceGroupName -Name $workspaceName -Location $location -Sku Standard

# Enable Microsoft Sentinel on the Log Analytics Workspace
Write-Host "Enabling Microsoft Sentinel..."
$sentinel = Set-AzOperationalInsightsIntelligencePack -ResourceGroupName $resourceGroupName -WorkspaceName $workspaceName -IntelligencePackName "AzureSecurityCenter" -Enabled $true

# Verify Sentinel is enabled
Write-Host "Verifying Microsoft Sentinel is enabled..."
Get-AzOperationalInsightsIntelligencePack -ResourceGroupName $resourceGroupName -WorkspaceName $workspaceName | Where-Object { $_.Name -eq "AzureSecurityCenter" }

# Create a sample analytic rule
Write-Host "Creating a sample analytic rule..."
$ruleName = "SampleRule"
$ruleQuery = @"
SecurityEvent
| where TimeGenerated > ago(1d)
| where EventID == 4625
"@

# Define the rule schedule
$ruleSchedule = @{
    FrequencyInMinutes  = 5
    TimeWindowInMinutes = 60
}

# Create the analytic rule
$rule = @{
    ResourceGroupName   = $resourceGroupName
    WorkspaceName       = $workspaceName
    Name                = $ruleName
    DisplayName         = "Sample Rule for Failed Logins"
    Description         = "This rule detects failed login attempts."
    Severity            = "High"
    Query               = $ruleQuery
    Enabled             = $true
    QueryFrequency      = [TimeSpan]::FromMinutes($ruleSchedule.FrequencyInMinutes)
    QueryPeriod         = [TimeSpan]::FromMinutes($ruleSchedule.TimeWindowInMinutes)
    TriggerOperator     = "GreaterThan"
    TriggerThreshold    = 5
    SuppressionDuration = [TimeSpan]::FromMinutes(0)
    SuppressionEnabled  = $false
    Tactics             = @("InitialAccess", "CredentialAccess")
}

New-AzOperationalInsightsSavedSearch -ResourceGroupName $resourceGroupName -WorkspaceName $workspaceName -Name $ruleName -DisplayName $rule.DisplayName -Category "Security" -Query $rule.Query -Version 1 -ScheduleFrequencyInMinutes $ruleSchedule.FrequencyInMinutes -ScheduleTimeWindowInMinutes $ruleSchedule.TimeWindowInMinutes -Enabled $rule.Enabled

# Deploying Data Connector (e.g., Azure Activity Logs)
Write-Host "Deploying Data Connector..."
$connectorName = "AzureActivity"
$connectorId = "/subscriptions/$((Get-AzContext).Subscription.Id)/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/providers/Microsoft.SecurityInsights/dataConnectors/$connectorName"

New-AzResource -ResourceId $connectorId -Properties @{}

Write-Host "Deployment complete. Microsoft Sentinel is now set up and ready to use."
