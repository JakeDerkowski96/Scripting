function Check-AzConnection {
    if ($null -eq $(Get-AzContext)) {
        try {
            $Conn = Connect-AzAccount
            if ($null -ne $Conn) {
                Write-Host -ForegroundColor "Successful authenticated with $($conn.Context.Account.Id)"                
            }
            else {
                Write-Host -ForegroundColor Red "Failed to authenticate to Azure"
            }
        }
        catch {
            Write-Host -ForegroundColor Red "Failed to authenticate to Azure"
        }        
    }
    else {
        Write-Host -ForegroundColor Green "A connection has already been established with $($conn.Context.Account.Type) to $($conn.Context.Account.Id)"
    }
}
