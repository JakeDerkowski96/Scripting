Function Remove-EmptyColumns {
    [Cmdletbinding()]
    Param(
        [Parameter(Mandatory=$true)]
        [string]$InputDirectory,
        $OutputDirectory
    )

    $extension = "*.csv"
    $TargetFiles = @()

    $A=(Get-ChildItem -Path $InputDirectory -Filter $extension -Recurse | Select-Object $_.FullName)
     $TargetFiles =+ $_.FullName



}