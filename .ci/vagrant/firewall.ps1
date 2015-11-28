. "C:\code\.ci\vagrant\functions.ps1"

Write-Output "Disabling firewall"
Run "netsh.exe" "advfirewall set private state off"
Run "netsh.exe" "advfirewall set domain state off"
Run "netsh.exe" "advfirewall set public state off"
