. "C:\code\.ci\vagrant\functions.ps1"

Write-Output "Disabling UAC (may require a reboot)"
New-ItemProperty `
    -Path HKLM:Software\Microsoft\Windows\CurrentVersion\policies\system `
    -Name EnableLUA -PropertyType DWord -Value 0 -Force

