. "C:\code\.ci\vagrant\functions.ps1"

Write-Output "Changing password policy"
SafeRun "secedit.exe" "/configure /db C:\windows\security\local.sdb /cfg C:\code\.ci\vagrant\system\files\secpol.cfg /areas SECURITYPOLICY"
SafeRun "gpupdate.exe" "/Force"
