. "C:\code\.ci\vagrant\functions.ps1"

$BASH = "C:\cygwin\bin\bash.exe"
$CODE = "/cygdrive/c/code/"
$items = Get-ChildItem C:\python -name

Run $BASH "--login -c 'mkdir -p /cygdrive/c/virtualenv'"

foreach ($pyversion in $items) {
    $virtualenv = "/cygdrive/c/python/$pyversion/Scripts/virtualenv.exe"
    Run $BASH "--login -c '$virtualenv virtualenv/$pyversion --clear'"
    Run $BASH "--login -c 'virtualenv/$pyversion/Scripts/python.exe C:\code\setup.py develop'"
}