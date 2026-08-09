$app = Get-AzureADApplication -ObjectId $id
$app.requiredResourceAccess | ConvertTo-Json -Depth 3

$sp = Get-AzureADServicePrincipal -All $true | Where-Object { $_.AppId -eq '00000003-0000-0000-c000-000000000000' }
$sp.AppRoles | Where-Object { $_.Id -eq '5b567255-7703-4780-807c-7be8301ae99b' }

$app = Get-AzureADApplication -ObjectId $Id
$appsp = Get-AzureADServicePrincipal -All $true | Where-Object { $_.AppId -eq $app.AppId }


New-AzResourceGroup -Name "RG-Dashboards" -Location "eastus"

@{parameters('Company Name') } - New Microsoft Sentinel Incident - @{triggerBody()?['object']?['properties']?['incidentNumber'] }-{ triggerBody()?['object']?['properties']?['title']}

Jason Mattox  I  o  214.655.1600  I  d  469.341.2360