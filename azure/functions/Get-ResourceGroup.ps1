#Check Resource Group Existing or not
Get-AzResourceGroup -Name $ResourceGroup -ErrorVariable notPresent -ErrorAction SilentlyContinue

if ($notPresent){        
    Write-Host "ResourceGroup $($ResourceGroup) associated to Log Analytics Workspace - not found"
    Write-Host "Exiting.................." -ForegroundColor Red
    break
}