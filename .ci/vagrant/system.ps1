. "C:\code\.ci\vagrant\functions.ps1"

Write-Output "Disabling firewall"
Run "netsh.exe" "advfirewall set private state off"
Run "netsh.exe" "advfirewall set domain state off"
Run "netsh.exe" "advfirewall set public state off"

Write-Output "Disabling UAC (may require a reboot)"
New-ItemProperty `
    -Path HKLM:Software\Microsoft\Windows\CurrentVersion\policies\system `
    -Name EnableLUA -PropertyType DWord -Value 0 -Force

Write-Output "Changing password policy"
Run "secedit.exe" "/configure /db C:\windows\security\local.sdb /cfg C:\code\.ci\vagrant\files\secpol.cfg /areas SECURITYPOLICY"
Run "gpupdate.exe" "/Force"