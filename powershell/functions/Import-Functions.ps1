function Import-Functions{
    param(
        [Parameter(Mandatory)][string]$functionPath
    )
    $functionFiles = Get-ChildItem -Path $functionPath -Filter "*.ps1"
    
    # loop an try to import the function
    foreach($file in $functionFiles){
        try {
            . $file.FullName
            Write-Verbose -Message "Successfully imported $($file.BaseName)"
            
        }
        catch {
            Write-Verbose -Message "Failed to import $($file.BaseName)"
        }
    }
}