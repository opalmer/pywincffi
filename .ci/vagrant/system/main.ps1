. "C:\code\.ci\vagrant\functions.ps1"

$DIR = Split-Path $MyInvocation.MyCommand.Path

RunScript "$DIR/uac.ps1"
RunScript "$DIR/firewall.ps1"
RunScript "$DIR/password-policy.ps1"
