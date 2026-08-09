function Test-TargetPath {

    param(
        [Parameter(Mandatory = $true)]$targetPath
    )

    while (!(Test-Path $targetPath)) {
        $targetPath = Read-Host "Please enter a valid path: "
    }   
}