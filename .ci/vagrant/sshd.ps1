. "C:\code\.ci\vagrant\functions.ps1"

$BASH = "C:\cygwin\bin\bash.exe"

# Uninstall the existing service first if one exists.  This ensures we get
# a clean slate every time.
Run $BASH "--login -c '/usr/bin/cygrunsrv --remove sshd'"
Run $BASH "--login -c '/bin/ssh-host-config --yes --name sshd --pwd 'vagrant'"

if (!(Test-Path -Path "C:\cygwin\home\users\vagrant\.ssh\" )) {
    Write-Output "Creating ~/.ssh/"
    Run $BASH "--login -c 'mkdir -p ~/.ssh/'"
    Run $BASH "--login -c 'chmod 700 ~/.ssh/'"
}

if ((Test-Path -Path "C:\code\.ci\vagrant\files\authorized_keys" )) {
    Write-Output "Copying C:\code\.ci\vagrant\files\authorized_keys to ~\.ssh\authorized_keys"
    $src = "/cygdrive/c/code/.ci/vagrant/files/authorized_keys"
    $dst = "/home/vagrant/.ssh/authorized_keys"
    Run $BASH "--login -c 'cp $src $dst"
    Run $BASH "--login -c 'chmod 644 $dst"
} else {
    Write-Output "C:\code\.ci\vagrant\files\authorized_keys does not exist"
}

# Replace the sshd configuration with our own
Write-Output "Replace SSHD configuration"
$src = "/cygdrive/c/code/.ci/vagrant/files/sshd_config"
$dst = "/etc/sshd_config"
Run $BASH "--login -c 'cp $src $dst"

RestartService "sshd"

