function Test-OutPath {
    param (
        [Parameter()][string]$Path
    )

    if!(Test-Path -Path $Path) {
        Write-Verbose -Message "$Path was not found, creating it now."
        try {
            New-Item -ItemType Directory -Path $Path | Out-Null
            Write-Host -ForegroundColor Greem "Created path: $Path "
        }
        catch {
            Write-Verbose -Message "Failed to create $Path"
        }
    }else {
        Write-Verbose -Message "$Path already exists"
    }
}