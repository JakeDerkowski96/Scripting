function CleanJson($data) {
    return $data -replace '\"', '"' | ConvertFrom-Json | ConvertTo-Json
}