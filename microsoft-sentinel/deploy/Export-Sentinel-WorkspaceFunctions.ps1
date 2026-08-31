param(
    [Parameter(Mandatory = $true)]$SubscriptionId,
    [Parameter(Mandatory = $true)]$ResourceGroup,
    [Parameter(Mandatory = $true)]$WorkspaceName,
    [Parameter()][string[]]$Categories
)

$SavedQueries = (Get-AzOperationalInsightsSavedSearch -ResourceGroupName $ResourceGroup -WorkspaceName $WorkspaceName).Value.Properties


Set-AzContext -Subscription $SubscriptionId


# Import Saved Searches
foreach ($search in $ExportedSearches) {
    $id = $search.Category + "|" + $search.DisplayName
    New-AzOperationalInsightsSavedSearch -Force -ResourceGroupName $ResourceGroup `
                -WorkspaceName $WorkspaceName `
                -SavedSearchId $id `
                -DisplayName $search.DisplayName `
                -Category $search.Category `
                -Query $search.Query `
                -Version $search.Version
}
