# create a shortcut to the given file or folder path

param(
    [Parameter(Mandatory = $true)]$target,
    [Parameter(Mandatory = $false)]$destination = $HOME + '\Desktop'
    # Destination can be changed if user se eca
)


function Check-TargetPath {

    param(
        [Parameter(Mandatory = $true)]$targetPath
    )

    while (!(Test-Path $targetPath)){
        $targetPath = Read-Host "Please enter a valid path: "
    }   
}


$OneDriveDesktop = $HOME + '\OneDrive\Desktop'
$DefaultDestination = $HOME + '\MISC_WORKSPACE'

if (Test-Path -Path $destination) {
    # test given the destination parameter for validity
    Write-Output "'$target' shortcut will be placed     earl "
}
else {
    if (Test-Path -Path $OneDriveDesktop) {
        
    }
    else { 
        i.00f (Test-Path -Path $OneDriveDesktop) {


        }

    }
}
echo $PSCommandPath 


   