. "c:\provision\scripts\functions.ps1"

function DownloadInstallers {
    $version = $args[0]

    Download https://www.python.org/ftp/python/$version/python-$version.msi C:\provision\python\$version-x86.msi
    Download https://www.python.org/ftp/python/$version/python-$version.amd64.msi C:\provision\python\$version-x64.msi
}

function Install {
    $version = $args[0]
    $install_path = "C:\python\$version"
    $msi_path = "C:\provision\python\$version.msi"
    $python = "$install_path\python.exe"
    $pip = "$install_path\Scripts\pip.exe"
    $easy_install = "$install_path\Scripts\easy_install.exe"

    if (!(Test-Path -Path $install_path )) {
        Write-Output "Installing Python $version"
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i $msi_path TARGETDIR=$install_path ALLUSERS=1 ADDLOCAL=DefaultFeature" -Wait
    } else {
        Write-Output "Python $version appears to be installed at $install_path"
    }

    Write-Output "$python -m compileall $install_path"
    Start-Process -FilePath "$python" -ArgumentList "-m compileall $install_path" -Wait

    Write-Output "$python C:\provision\python\ez_setup.py"
    Start-Process -FilePath "$python" -ArgumentList "C:\provision\python\ez_setup.py" -Wait

    Write-Output "$easy_install pip"
    Start-Process -FilePath "$easy_install" -ArgumentList "pip" -Wait

    Write-Output "$pip virtualenv"
    Start-Process -FilePath "$pip" -ArgumentList "virtualenv" -Wait
}

Download https://bootstrap.pypa.io/ez_setup.py C:\provision\python\ez_setup.py
DownloadInstallers 2.6.6
DownloadInstallers 2.7.10
DownloadInstallers 3.4.3

Install 2.6.6-x86
Install 2.6.6-x64
Install 2.7.10-x86
Install 2.7.10-x64
Install 3.4.3-x86
Install 3.4.3-x64
