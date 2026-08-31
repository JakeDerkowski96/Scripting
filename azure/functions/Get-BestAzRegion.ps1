Connect-AzAccount 

Get-AzLocation | Sort-Object {[math]::Sqrt(([double]$_.Latitude - [double]$latitude) * ([double]$_.Latitude - [double]$latitude) + ([double]$_.Longitude - [double]$longitude) * ([double]$_.Longitude - [double]$longitude))})[0].DisplayName