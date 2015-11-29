. "C:\code\.ci\vagrant\functions.ps1"

#
# Sets up the authorized_keys file for the
# Vagrant use.  This should allow ssh from
# the local system to work correctly, assuming
# a custom authorized_keys is supplied.
#

SafeRun $BASH "--login -c 'mkdir -p ~/.ssh/'"
SafeRun $BASH "--login -c 'chmod 700 ~/.ssh/'"

if ((Test-Path -Path "C:\code\.ci\vagrant\sshd\files\authorized_keys" )) {
    Write-Output "Copying C:\code\.ci\vagrant\sshd\files\authorized_keys to ~\.ssh\authorized_keys"
    $src = "/cygdrive/c/code/.ci/vagrant/sshd/files/authorized_keys"
    $dst = "/home/vagrant/.ssh/authorized_keys"
    SafeRun $BASH "--login -c 'cp $src $dst"
    SafeRun $BASH "--login -c 'chmod 644 $dst"
} else {
    Write-Output "C:\code\.ci\vagrant\sshd\files\authorized_keys does not exist"
}
