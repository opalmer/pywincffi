. "C:\code\.ci\vagrant\functions.ps1"

#
# Disables User Account Control (UAC) which will prevent
# certain actions from executing in an unattended fashion.
#

New-ItemProperty `
    -Path HKLM:Software\Microsoft\Windows\CurrentVersion\policies\system `
    -Name EnableLUA -PropertyType DWord -Value 0 -Force

