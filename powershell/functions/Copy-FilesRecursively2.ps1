function Copy-FilesRecursively {
    param (
        [string]$SourceDirectory,
        [string]$OutputDirectory
    )

    # Create the output directory if it doesn't exist
    if (-not (Test-Path -Path $OutputDirectory)) {
        New-Item -ItemType Directory -Path $OutputDirectory | Out-Null
    }

    # Get all files recursively from the source directory
    $files = Get-ChildItem -Path $SourceDirectory -File -Recurse

    foreach ($file in $files) {
        # Construct the destination path in the output directory
        $destinationPath = Join-Path -Path $OutputDirectory -ChildPath $file.Name

        # Copy the file to the output directory
        Copy-Item -Path $file.FullName -Destination $destinationPath -Force
    }

    Write-Host "All files copied to $OutputDirectory."
}

# Example usage:
$sourceDir = "C:\Users\derko\OneDrive - derkcloudsec.com\myDownloads\Detections\Detections"
$outputDir = "C:\Users\derko\OneDrive - derkcloudsec.com\Sentinel\Detections"
Copy-FilesRecursively -SourceDirectory $sourceDir -OutputDirectory $outputDir
