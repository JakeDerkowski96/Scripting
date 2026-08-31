function Build-FilesFromContent {

    [CmdletBinding()]
    param (
        [Parameter()][string]
        $PathToContent
            
    )


    $content = Get-Content -raw -Path $PathToContent
    $pattern = 'your-regex-pattern'
    $lines = $content -split '\n'
    $variables = @{}
    foreach ($line in $lines) {
        # beginning of file
        if ($line -match $pattern) {
            $var_name = $line.Trim()
            $variables[$var_name] = @()
        }
        else {
            $variables[$var_name] += $line
        }
    }
    foreach ($var_name in $variables.Keys) {
        Set-Content -Path "$var_name.txt" -Value ($variables[$var_name] -join "`n")
    }
}