. "c:\provision\scripts\functions.ps1"

function Install {
    $version = $args[0]
    $install_path = "C:\python\$version"
    $msi_path = "C:\provision\python\$version.msi"
    $python = "$install_path\python.exe"
    $pip = "$install_path\Scripts\pip.exe"
    $easy_install = "$install_path\Scripts\easy_install.exe"

    if (!(Test-Path -Path $install_path )) {
        Write-Output "Installing Python $version"
        Run "msiexec.exe" "/i $msi_path TARGETDIR=$install_path ALLUSERS=1 ADDLOCAL=DefaultFeature"
    } else {
        Write-Output "Python $version appears to be installed at $install_path"
    }

    Run "$python" "-m compileall $install_path"
    Run "$python" "C:\provision\python\ez_setup.py"
    Run "$easy_install" "pip"
    Run "$pip" "virtualenv"
}

Install "2.6.6-x86"
Install "2.6.6-x64"
Install "2.7.10-x86"
Install "2.7.10-x64"
Install "3.4.3-x86"
Install "3.4.3-x64"
