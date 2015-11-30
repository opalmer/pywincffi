. "C:\code\.ci\vagrant\functions.ps1"

#
# Installs the pywincffi code base.
#

$items = Get-ChildItem C:\cygwin\home\vagrant\virtualenv -name

SafeRun $BASH "--login -c 'rm -rf code && rsync -r /cygdrive/c/code/ code/ --exclude `".*`"'"

# FIXME: The below does not work for all interpreters.  Probably need to setup
# a wrapper script just like we have to for appveyor.

# FIXME: Don't use bash, setup/execute python directly via powershell
foreach ($virtualenv_name in $items) {
    $python = "/home/vagrant/virtualenv/$virtualenv_name/Scripts/python.exe"

    # NOTE: We're running in cygwin but we're really executing a Windows
    # binary.  So as a result we have to pass in the Windows path for
    # the code with forward slashes.
    SafeRun $BASH "--login -c 'cd code && $python setup.py test'"
}
