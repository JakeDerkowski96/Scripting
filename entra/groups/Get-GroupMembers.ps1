Function Get-GroupMembers {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [string]
        $GroupId,
        $ResultsPath
    )
    Connect-AzureAD
    
    
    $GroupDetails = Get-AzureADGroupMember -ObjectId $GroupId
    $resultsarray = @()

    $UserObject = new-object PSObject
    $UserObject | add-member  -membertype NoteProperty -name "Group Name" -Value $GroupDetails.DisplayName
    $UserObject | add-member  -membertype NoteProperty -name "Member Name" -Value $GroupDetails.DisplayName
    $UserObject | add-member  -membertype NoteProperty -name "ObjType" -Value $GroupDetails.ObjectType
    $UserObject | add-member  -membertype NoteProperty -name "UserType" -Value $GroupDetails.UserType
    $UserObject | add-member  -membertype NoteProperty -name "UserPrinicpalName" -Value $GroupDetails.UserPrincipalName
    $resultsarray += $UserObject

    $resultsarray | Export-Csv -Encoding UTF8  -Delimiter "," -Path $ResultsPath -NoTypeInformation
}