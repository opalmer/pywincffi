. "c:\code\.ci\vagrant\functions.ps1"

#
# Installs the core Python interpreters.
#

function Install($version, $product_id) {
    $install_path = "C:\python\$version"
    $msi_path = "C:\provision\python\$version.msi"

    if (!(ProductInstalled $product_id)) {
        Write-Output "Installing Python $version"
        SafeRun "msiexec.exe" "/i $msi_path TARGETDIR=$install_path ALLUSERS=1 ADDLOCAL=DefaultFeature"
    } else {
        Write-Output "Python $version appears to already be installed"
    }
}

function DownloadPythonInstallers($version) {
    # 32-bit
    Download "https://www.python.org/ftp/python/$version/python-$version.msi" "C:\provision\python\$version-x86.msi"

    # 64-bit
    Download "https://www.python.org/ftp/python/$version/python-$version.amd64.msi" "C:\provision\python\$version-x64.msi"
}

DownloadPythonInstallers "2.6.6"
DownloadPythonInstallers "2.7.10"
DownloadPythonInstallers "3.4.3"

Install "2.6.6-x86" "{6151CF20-0BD8-4023-A4A0-6A86DCFE58E5}"
Install "2.6.6-x64" "{6151CF20-0BD8-4023-A4A0-6A86DCFE58E6}"
Install "2.7.10-x86" "{E2B51919-207A-43EB-AE78-733F9C6797C2}"
Install "2.7.10-x64" "{E2B51919-207A-43EB-AE78-733F9C6797C3}"
Install "3.4.3-x86" "{CCD588A7-8D55-49F1-A30C-47FAB40889ED}"
Install "3.4.3-x64" "{9529565F-E693-3F11-B3BF-8CD545F5F9A0}"
