Function Test-Existence {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [ValidateSet('File', 'Directory')][string]$ItemType,
        [string]$ItemPath
    )
    if (!(Test-Path -Path $ItemPath)) {
        Write-Verbose -Message "Creating $($ItemType): $($ItemPath)"
        New-Item -ItemType $ItemType -Path $ItemPath | Out-Null
    }
    else {
        Write-Verbose -Message "$($ItemPath)"
        
    }
}