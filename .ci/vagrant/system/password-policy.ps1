. "C:\code\.ci\vagrant\functions.ps1"

#
# Changes the password policies so we don't run into
# issues when using the default 'vagrant' password.
#

SafeRun "secedit.exe" "/configure /db C:\windows\security\local.sdb /cfg C:\code\.ci\vagrant\system\files\secpol.cfg /areas SECURITYPOLICY"
SafeRun "gpupdate.exe" "/Force"
