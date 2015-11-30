. "C:\code\.ci\vagrant\functions.ps1"

#
# Builds the core virtual environments in Vagrant's
# home directory.
#

$CODE = "/cygdrive/c/code/"
$items = Get-ChildItem C:\python -name

foreach ($pyversion in $items) {
    $virtualenv = "/cygdrive/c/python/$pyversion/Scripts/virtualenv.exe"
    $target = "virtualenv/$pyversion"

    SafeRun $BASH "--login -c 'rm -rf $target'"
    SafeRun $BASH "--login -c '$virtualenv virtualenv/$pyversion'"
}
