# this is not my code, but I may need to use it here pretty sooon.
# https://stackoverflow.com/questions/25767850/how-do-i-correctly-serialize-a-psobject-with-a-datetime-into-json
function ConvertTo-JsonifiablePSObject
{
    param
    (
        [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
        [PSObject]$Object
    )

    $newObjectProperties = @{}

    foreach ($property in $Object.psobject.properties)
    {
        $value = $property.Value

        if ($property.TypeNameOfValue -eq "System.Management.Automation.PSCustomObject")
        {
            $value = ConvertTo-JsonifiablePSObject -Object $property.Value
        }
        elseif ($property.TypeNameOfValue -eq "System.DateTime")
        {
            $value = $property.Value.ToString("yyyy'-'MM'-'dd'T'HH':'mm':'ss.fffffffK")
        }

        $newObjectProperties[$property.Name] = $value
    }

    return New-Object -TypeName PSObject -Property $newObjectProperties
}