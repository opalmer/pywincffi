. "C:\code\.ci\vagrant\functions.ps1"

#
# Installs the pywincffi code base.
#

$items = Get-ChildItem C:\cygwin\home\vagrant\virtualenv -name
$ez_setup = "/cygdrive/c/provision/python/ez_setup.py"

foreach ($virtualenv_name in $items) {
    $pip = "virtualenv/$virtualenv_name/Scripts/pip.exe"

    # NOTE: We're running in cygwin but we're really executing a Windows
    # binary.  So as a result we have to pass in the Windows path for
    # pywincffi with forward slashes.
    SafeRun $BASH "--login -c '$pip install -e C:/code/'"
}
