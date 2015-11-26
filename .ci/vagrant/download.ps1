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
        Write-Output "(skipped) Downloading $url to $output"
    }
}

function DownloadPythonInstallers {
    $version = $args[0]

    Download https://www.python.org/ftp/python/$version/python-$version.msi C:\provision\python\$version-x86.msi
    Download https://www.python.org/ftp/python/$version/python-$version.amd64.msi C:\provision\python\$version-x64.msi
}


Download https://bootstrap.pypa.io/ez_setup.py C:\provision\python\ez_setup.py
DownloadPythonInstallers 2.6.6
DownloadPythonInstallers 2.7.10
DownloadPythonInstallers 3.4.3
Download "http://download.microsoft.com/download/8/B/5/8B5804AD-4990-40D0-A6AA-CE894CBBB3DC/VS2008ExpressENUX1397868.iso" C:\provision\visual_studio\VS2008ExpressENUX1397868.iso
Download "http://download.microsoft.com/download/1/E/5/1E5F1C0A-0D5B-426A-A603-1798B951DDAE/VS2010Express1.iso" C:\provision\visual_studio\VS2010Express1.iso
