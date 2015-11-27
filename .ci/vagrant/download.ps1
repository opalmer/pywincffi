function Download {
    $url = $args[0]
    $output = $args[1]
    $parent_dir = Split-Path $output -parent
    $start_time = Get-Date

    if (!(Test-Path -Path $parent_dir )) {
        Write-Output "Creating $parent_dir"
        New-Item -ItemType directory -Path $parent_dir
    }

    if (!(Test-Path -Path $output )) {
        Write-Output "Downloading $url to $output"
        $wc = New-Object System.Net.WebClient
        $wc.DownloadFile($url, $output)
    } else {
        Write-Output "Already downloaded $url"
    }
}

function DownloadPythonInstallers {
    $version = $args[0]

    Download https://www.python.org/ftp/python/$version/python-$version.msi C:\provision\python\$version-x86.msi
    Download https://www.python.org/ftp/python/$version/python-$version.amd64.msi C:\provision\python\$version-x64.msi
}

DownloadPythonInstallers 2.6.6
DownloadPythonInstallers 2.7.10
DownloadPythonInstallers 3.4.3
Download "https://cygwin.com/setup-x86_64.exe" "C:\provision\cygwin\setup-x86_64.exe"
Download "https://bootstrap.pypa.io/ez_setup.py" "C:\provision\python\ez_setup.py"
Download "https://download.microsoft.com/download/1/1/1/1116b75a-9ec3-481a-a3c8-1777b5381140/vcredist_x86.exe" "C:\provision\vc_redist\2008x86.exe"
Download "https://download.microsoft.com/download/d/2/4/d242c3fb-da5a-4542-ad66-f9661d0a8d19/vcredist_x64.exe" "C:\provision\vc_redist\2008x64.exe"
Download "https://download.microsoft.com/download/5/B/C/5BC5DBB3-652D-4DCE-B14A-475AB85EEF6E/vcredist_x86.exe" "C:\provision\vc_redist\2010x86.exe"
Download "https://download.microsoft.com/download/3/2/2/3224B87F-CFA0-4E70-BDA3-3DE650EFEBA5/vcredist_x64.exe" "C:\provision\vc_redist\2010x64.exe"
Download "https://download.microsoft.com/download/8/B/5/8B5804AD-4990-40D0-A6AA-CE894CBBB3DC/VS2008ExpressENUX1397868.iso" "C:\provision\visual_studio\VS2008ExpressENUX1397868.iso"
Download "https://download.microsoft.com/download/1/E/5/1E5F1C0A-0D5B-426A-A603-1798B951DDAE/VS2010Express1.iso" "C:\provision\visual_studio\VS2010Express1.iso"
Download "https://download.microsoft.com/download/6/2/A/62A76ABB-9990-4EFC-A4FE-C7D698DAEB96/9600.17050.WINBLUE_REFRESH.140317-1640_X64FRE_SERVER_EVAL_EN-US-IR3_SSS_X64FREE_EN-US_DV9.ISO" "C:\provision\2012r2.iso"
