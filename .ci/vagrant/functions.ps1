function Download($url, $output) {
    $parent_dir = Split-Path $output -parent
    $start_time = Get-Date

    if (!(Test-Path -Path $parent_dir )) {
        Write-Output "Creating $parent_dir"
        New-Item -ItemType directory -Path $parent_dir
    }

    if (!(Test-Path -Path $output )) {
        Write-Output "Downloading $url to $output"
        $client = New-Object System.Net.WebClient
        $client.DownloadFile($url, $output)
    } else {
        Write-Output "Already downloaded $url"
    }
}

function RunScript($script) {
    Write-Output "[starting] $script"
    & $script
    Write-Output "[finished] $script"
}

function RestartService($service_name) {
    $service = Get-Service $service_name

    if ($service.Length -ne 1) {
        Write-Warning "Service $service_name does not exist"
        Exit 1
    }

    if ($service.Status -eq "Running") {
        "Stopping service $service_name"
        Stop-Service $service_name
    }

    "Starting service $service_name"
    Start-Service $service_name
}

function Run($filename, $arguments) {
    Write-Output "run: $filename $arguments"
    $start_info = New-object System.Diagnostics.ProcessStartInfo
    $start_info.CreateNoWindow = $true
    $start_info.UseShellExecute = $false
    $start_info.RedirectStandardOutput = $true
    $start_info.RedirectStandardError = $true
    $start_info.FileName = $filename
    $start_info.Arguments = $arguments
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $start_info
    [void]$process.Start()
    $output = $process.StandardOutput.ReadToEnd()
    $process.WaitForExit()
    $code = $process.ExitCode
    $output

    # We don't really care about the exit code in most
    # cases so we'll just print it.
    Write-Output "exit code: $code"
}
