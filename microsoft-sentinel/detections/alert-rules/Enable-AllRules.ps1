### assuming you have defined a hash table containg the sentinel workspace details like:
<#
$SentinelParams = @{
    SubscriptionId = $DerkCloud.SubscriptionId
    ResourceGroupName = $DerkCloud.ResourceGroup
    WorkspaceName = $DerkCloud.Workspace
}
#>

$AllRules = Get-AzSentinelAlertRule @SentinelParams

foreach($rule in $AllRules){
    switch ($rule.Kind) {
        "Scheduled" {
            Update-AzSentinelAlertRule @SentinelParams -RuleId $rule.Id -Scheduled -Enabled
        }

        "NRT" {
            Update-AzSentinelAlertRule @SentinelParams -RuleId $rule.Id -NRT -Enabled
        }

        "FusionMLorTI" {
            Update-AzSentinelAlertRule @SentinelParams -RuleId $rule.Id -FusionMLorTI -Enabled
        }

        "MicrosoftSecurityIncidentCreation" {
            Update-AzSentinelAlertRule @SentinelParams -RuleId $rule.Id -MicrosoftSecurityIncidentCreation -Enabled
        }
    }
}