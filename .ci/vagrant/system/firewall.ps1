. "C:\code\.ci\vagrant\functions.ps1"

Write-Output "Disabling firewall"
SafeRun "netsh.exe" "advfirewall set private state off"
SafeRun "netsh.exe" "advfirewall set domain state off"
SafeRun "netsh.exe" "advfirewall set public state off"
