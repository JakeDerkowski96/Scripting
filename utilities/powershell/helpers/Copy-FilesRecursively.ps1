function Copy-FilesRecursively {
    <#
    .EXAMPLE
    # Copy-FilesRecursively -inputDirectory "C:\source" -outputDirectory "D:\destination
    #>
    param (
        [string]$inputDirectory,
        [string]$outputDirectory
    )

    # Create the output directory if it doesn't exist
    if (!(Test-Path -Path $outputDirectory)) {
        New-Item -ItemType Directory -Path $outputDirectory | Out-Null
    }

    # Recursively copy files from input to output
    Get-ChildItem -Path $inputDirectory -Recurse | ForEach-Object {
        $destinationPath = Join-Path -Path $outputDirectory -ChildPath $_.FullName.Substring($inputDirectory.Length)

        # Check if basename length exceeds 63 characters
        if ($_.BaseName.Length -gt 63) {
            $slicedBasename = $_.BaseName.Substring(0, 54)
            $newFileName = $slicedBasename + $_.Extension
            $destinationPath = Join-Path -Path $outputDirectory -ChildPath $newFileName
        }

        Copy-Item -Path $_.FullName -Destination $destinationPath -Force
    }

    Write-Host "Files copied successfully!"
}
