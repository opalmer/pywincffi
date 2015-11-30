. "C:\code\.ci\vagrant\functions.ps1"

#
# Installs cygwin (but does not configure it).
#

if (!(Test-Path -Path "C:\cygwin")) {
    Download "https://cygwin.com/setup-x86_64.exe" "C:\provision\cygwin\setup-x86_64.exe"

    Write-Output "Installing cygwin"
    $args = "--quiet-mode --verbose --no-shortcuts --no-desktop --local-package-dir C:\provision\cygwin\packages\ --root C:\cygwin\ --site http://mirrors.kernel.org/sourceware/cygwin/ --packages openssh,bash,rsync"
    Run "C:\provision\cygwin\setup-x86_64.exe" $args

} else {
    Write-Output "cygwin appears to already be installed"
}
