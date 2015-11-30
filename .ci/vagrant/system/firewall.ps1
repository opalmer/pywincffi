. "C:\code\.ci\vagrant\functions.ps1"

#
# Configures the Windows firewall with an open
# policy.
#

SafeRun "netsh.exe" 'advfirewall firewall add rule name="SSHD" dir=in action=allow protocol=TCP localport=22'
SafeRun "netsh.exe" 'advfirewall firewall add rule name="Remote Desktop" dir=in action=allow protocol=TCP localport=3389'
SafeRun "netsh.exe" 'advfirewall firewall add rule name="WinRM" dir=in action=allow protocol=TCP localport=5985'
SafeRun "netsh.exe" 'advfirewall firewall add rule name="WinRM" dir=in action=allow protocol=TCP localport=5986'
