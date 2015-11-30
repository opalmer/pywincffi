$SOFTWARE = Get-WmiObject -Class Win32_Product
$BASH = "C:\cygwin\bin\bash.exe"

function ProductInstalled($ident) {
    foreach ($software in $SOFTWARE) {
        if ($software.IdentifyingNumber -eq $ident) {
            return $True
        }
    }
    return $False
}

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
    }
}

function RunScript($script) {
    if (!(Test-Path -Path $script )) {
        Write-Output "No such file $script"
        Exit 1
    }

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

function SafeRun($filename, $arguments) {
    Run $filename $arguments $False
}

function Run($filename, $arguments, $IgnoreExit=$True) {
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

    if (($IgnoreExit -eq $False) -and ($code -ne 0)) {
        Write-Warning "Exit code was non-zero"
        Exit $code
    }
}
