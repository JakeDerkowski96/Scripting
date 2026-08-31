# Get List of Registered Azure AD Applications using PowerShell
Connect-AzureAD

# list all the applications that are registered by your company
Get-AzureADApplication -All:$true

# Get all apps including the Enterprise applications (Get all service principals)
Get-AzureADServicePrincipal -All:$true | ? { $_.Tags -eq "WindowsAzureActiveDirectoryIntegratedApp" }

# filter by display name
Get-AzureADApplication -Filter "DisplayName eq 'TestAppName'"
# filter by application id
Get-AzureADApplication -Filter "AppId eq 'ca066717-5ded-411b-879e-741de0880978'"

# Find and list only Web applications
Get-AzureADApplication -All:$true | Where-Object { $_.PublicClient -ne $true } | FT
# Find and list Native applications alone 
Get-AzureADApplication -All:$true | Where-Object { $_.PublicClient -eq $true } | FT

# Export All Registered Azure AD Application Details to CSV 
Get-AzureADApplication -All:$true |
Select-Object DisplayName, AppID, PublicClient, AvailableToOtherTenants, HomePage, LogoutUrl  |
Export-Csv "C:\AzureADApps.csv"  -NoTypeInformation -Encoding UTF8

