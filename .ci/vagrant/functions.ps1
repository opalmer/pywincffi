function Download {
    $url = $args[0]
    $output = $args[1]
    $parent_dir = Split-Path $output -parent

    if (!(Test-Path -Path $parent_dir )) {
        Write-Output "Creating $parent_dir"
        New-Item -ItemType directory -Path $parent_dir
    }

    if (!(Test-Path -Path $output )) {
        Write-Output "Downloading $url to $output"
        Invoke-WebRequest $url -OutFile $output
    } else {
        Write-Output "Downloading $url to $output (skipped, file exists)"
    }
}
