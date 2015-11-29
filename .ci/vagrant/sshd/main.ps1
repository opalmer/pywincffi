. "C:\code\.ci\vagrant\functions.ps1"

$DIR = Split-Path $MyInvocation.MyCommand.Path

RunScript "$DIR\sshd.ps1"
RunScript "$DIR\authorized-keys.ps1"
