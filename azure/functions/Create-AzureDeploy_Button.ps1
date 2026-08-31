## Deploy Button

### Encode the Url

$url = "Link to raw github file"
[uri]::EscapeDataString($url)


[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/<encoded link here>)