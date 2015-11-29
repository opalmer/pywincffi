. "C:\code\.ci\vagrant\functions.ps1"

#
# Installs the core Python packages such as setuptools,
# pip and virtualenv.
#

Download "https://bootstrap.pypa.io/ez_setup.py" "C:\provision\python\ez_setup.py"

$items = Get-ChildItem C:\python -name
$ez_setup = "/cygdrive/c/provision/python/ez_setup.py"

foreach ($pyversion in $items) {
    $pyroot = "/cygdrive/c/python/$pyversion"
    $python = "$pyroot/python.exe"
    $easy_install = "$pyroot/Scripts/easy_install.exe"
    $pip = "$pyroot/Scripts/pip.exe"

    # NOTE: We're running in cygwin but we're really executing a Windows
    # binary.  So as a result we have to pass in the Windows path for
    # ez_setup with forward slashes.
    SafeRun $BASH "--login -c '$python C:/provision/python/ez_setup.py'"
    SafeRun $BASH "--login -c '$easy_install pip'"
    SafeRun $BASH "--login -c '$pip install --upgrade virtualenv pip'"
}
