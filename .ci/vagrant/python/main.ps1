. "C:\code\.ci\vagrant\functions.ps1"

$DIR = Split-Path $MyInvocation.MyCommand.Path

RunScript "$DIR\core-packages.ps1"
RunScript "$DIR\virtualenv.ps1"
