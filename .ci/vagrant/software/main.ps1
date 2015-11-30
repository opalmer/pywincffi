. "C:\code\.ci\vagrant\functions.ps1"

$DIR = Split-Path $MyInvocation.MyCommand.Path

RunScript "$DIR/cygwin.ps1"
RunScript "$DIR/visual-studio.ps1"
RunScript "$DIR/python.ps1"
