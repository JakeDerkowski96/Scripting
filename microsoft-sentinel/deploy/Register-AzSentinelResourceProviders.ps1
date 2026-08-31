Login-AzAccount # The browser will popup for creds

# Selected Subscription
Select-AzSubscription -SubscriptionId "put your sub id"

Register-AzResourceProvider -ProviderNamespace Microsoft.ManagedServices    # Azure Lighthouse
Register-AzResourceProvider -ProviderNamespace Microsoft.SecurityInsights   # Azure Sentinel
Register-AzResourceProvider -ProviderNamespace Microsoft.Notebooks          # Azure Notebooks
Register-AzResourceProvider -ProviderNamespace Microsoft.OperationalInsights 