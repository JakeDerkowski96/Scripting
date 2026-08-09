# requires Az.OperationalInsights
Function Deploy-LogAnalytics{
    Param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][string]$TenantId,
        [Parameter(Mandatory)][string]$SubscriptionId
        # or [Parameter(Mandatory)][string]$ResourceId
    )
}



# create log analytics workspace
New-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName

# enable sentinel 
Set-AzSentinel -WorkspaceName $WorkspaceName -ResourceGroupName $ResourceGroupName
