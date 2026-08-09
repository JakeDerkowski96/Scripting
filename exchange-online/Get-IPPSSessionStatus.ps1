fucntion Get-IPPSSessionConnectionStatus {
    $ConnectionCheck = (Get-PSSession | Where-Object {$_.ConfigurationName -eq 'Microsoft.Exchange'})

    if ($null -eq $ConnectionCheck){
        Write-Host "Please create a IPPSSession and rerun this script."
        Exit
    }
    else {
        Write-Host "$($ConnectionCheck.ComputerName) has been connected to $($ConnectionCheck.ConfigurationName)"
    }
}