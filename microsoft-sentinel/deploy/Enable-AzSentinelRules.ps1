# Enable-AzSentienlRuleTemplates.ps1

$Tenant = @{
    Tenant         = ""
    TenantId       = ""
    Workspace      = ""
    WorkspaceId    = ""
    ResourceGroup  = ""
    Subscription   = ""
    SubscriptionId = ""
    ResourceId     = ""
}

Import-Module Az.Accounts
Import-Module Az.SecurityInsights

Connect-AzAccount -TenantId $Tenant.TenantId

# $ruleTemplates = Get-AzSentinelAlertRuleTemplates -SubscriptionId $Tenant.SubscriptionId -WorkspaceName $Tenant.Workspace 

$existingRules = Get-AzSentinelAlertRule -SubscriptionId $Tenant.SubscriptionId -WorkspaceName $Tenant.Workspace -ResourceGroupName $Tenant.ResourceGroup

foreach ($rule in $existingRules) {
    if ($rule.Kind -eq "Scheduled") {
        Update-AzSentinelAlertRule -RuleId $rule.Id -SubscriptionId $Tenant.SubscriptionId -WorkspaceName $Tenant.Workspace -ResourceGroupName $Tenant.ResourceGroup -Scheduled -Enabled

    }
} 