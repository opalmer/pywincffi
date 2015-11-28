. ".ci/vagrant/functions.ps1"

if (!(Test-Path -Path "C:\cygwin")) {
    Write-Output "Installing cygwin"
    $args = "--quiet-mode --verbose --no-shortcuts --no-desktop --local-package-dir C:\provision\cygwin\packages\ --root C:\cygwin\ --site http://mirrors.kernel.org/sourceware/cygwin/ --packages openssh,bash"
    Run "C:\provision\cygwin\setup-x86_64.exe" $args

} else {
    Write-Output "cygwin appears to be installed"
}
