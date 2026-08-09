param(
    [Parameter(Mandatory=$true)]
    [string]$DirectoryPath,
    [Parameter(Mandatory=$true)]
    [string]$UserPrincipalName,
    [Parameter(Mandatory=$true)]
    [string]$RecipientAddress
)

$EmailSubjectPrefix = "DLP Policy test: "
$EmailBody = "Enter the desired email body text here"

Import-Module ExchangeOnlineManagement
Connect-ExchangeOnline -UserPrincipalName $UserPrincipalName

$VerbosePreference = "Continue"

Write-Verbose "Connecting to Exchange Online using $UserPrincipalName"
Write-Verbose "Directory path is $DirectoryPath"

foreach ($file in Get-ChildItem $DirectoryPath) {
    Write-Verbose "Sending email: $($EmailSubjectPrefix + $file.Name) as $UserPrincipalName to $RecipientAddress..."
    try {
        Send-MailMessage -From $UserPrincipalName -To $RecipientAddress -Subject ($EmailSubjectPrefix + $file.Name) -Attachments $file.FullName -Body $EmailBody -Verbose:$true
        Write-Host "Email was delivered successfully"
    }
    catch {
        Write-Host "Failed to send email: $($EmailSubjectPrefix + $file.Name). Error code: $($Error[0].Exception.ErrorCode). Error message: $($Error[0].Exception.Message)"
    }
    .
    
}

# ```powershell
# .\script.ps1 -DirectoryPath C:\path\to\directory -UserPrincipalName user@contoso.com -RecipientAddress recipient@contoso.com -Verbose
# ```
