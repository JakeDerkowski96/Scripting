# function to install all items in text file

[CmdletBinding()]
param (
    # path to file 
    [Parameter(Mandatory=$true)]
    [string]
    $ExtensionsFile    
)

$ExtensionArray = (Get-Content -Path $ExtensionsFile)
$ExtensionArray
Write-Host ""

<#
.SYNOPSIS
    Prompts user for answer to a yes no prompt.
.DESCRIPTION
    The user is prompted with the argument, and asked for a reply.
    If the reply matches YES or NO (case insensitive) the value is true
    or false.  Otherwise, the user is prompted again.
#>
function ask-user {
    [CmdletBinding()]
    Param (
        [Parameter(Mandatory = $true)]
        [string] $question
    )
    Process {
        $answer = read-Host $question
        if ("YES", "YE", "Y" -contains $answer) { $true }
        elseif ("NO", "N" -contains $answer) { $false }
        else { ask-user $question }
    }
} # End function ask-user



if ((ask-user -question "Install these extensions?") -eq $true){    
    foreach ($item in $ExtensionArray){
        code --install-extension $item        
    }
}