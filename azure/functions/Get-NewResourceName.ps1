# kinda the old idea below, but will use when creating the proper name, per the defined naming convention to be used in parameter json file/ARM Parameter file

param(
    [Parameter(Mandatory = $true)]$ResourceGroup,
    [Parameter(Mandatory = $true)]$Prefix
)

# Define Playbook naming convention here
function New-PbName() {
    param(
        [Parameter(Mandatory = $true)]$Prefix,
        [Parameter(Mandatory = $true)]$PlaybookName
    )

    # Naming convention example
    $NewName = $Prefix + "." + $PlaybookName
    return $NewName
}
