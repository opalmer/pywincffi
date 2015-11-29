. "C:\code\.ci\vagrant\functions.ps1"

#
# Configures and installs Cygwin's SSH
# server.
#

# Replace ssh-host-config with our own.  The only difference
# is ours spits out logs to /var/log instead of the Windows
# event log system.
$src = "/cygdrive/c/code/.ci/vagrant/sshd/files/ssh-host-config"
$dst = "/usr/bin/ssh-host-config-modified"

# Uninstall the existing service first if one exists.  This ensures we get
# a clean slate every time.
SafeRun $BASH "--login -c 'cp $src $dst'"
SafeRun $BASH "--login -c '/usr/bin/cygrunsrv --stop sshd'"
SafeRun $BASH "--login -c '/usr/bin/cygrunsrv --remove sshd'"
SafeRun $BASH "--login -c '/usr/bin/ssh-host-config-modified --yes --name sshd --pwd 'vagrant'"

# Replace the sshd configuration with our own
Write-Output "Replace SSHD configuration"
$src = "/cygdrive/c/code/.ci/vagrant/sshd/files/sshd_config"
$dst = "/etc/sshd_config"
SafeRun $BASH "--login -c 'cp $src $dst"

RestartService "sshd"
