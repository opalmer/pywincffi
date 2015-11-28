. "C:\code\.ci\vagrant\functions.ps1"

# Setup sshd (needed for remote intrepreters)
$service = Get-Service -Name sshd -ErrorAction SilentlyContinue
if ($service.Length -eq 0) {
    Write-Output "Configuring sshd"
    $args = "--login -c '/bin/ssh-host-config--yes --name sshd --pwd vagrant'"
    Run "C:\cygwin\bin\bash.exe" $args
}

if (!(Test-Path -Path "C:\cygwin\home\users\vagrant\.ssh\" )) {
    Write-Output "Creating ~/.ssh/"
    Run "C:\cygwin\bin\bash.exe" "--login -c 'mkdir -p ~/.ssh/'"
    Run "C:\cygwin\bin\bash.exe" "--login -c 'chmod 700 ~/.ssh/'"
}

if ((Test-Path -Path "C:\code\.ci\vagrant\files\authorized_keys" )) {
    Write-Output "Copying C:\code\.ci\vagrant\files\authorized_keys to ~\.ssh\authorized_keys"
    $src = "/cygdrive/c/code/.ci/vagrant/files/authorized_keys"
    $dst = "/home/vagrant/.ssh/authorized_keys"
    Run "C:\cygwin\bin\bash.exe" "--login -c 'cp $src $dst"
    Run "C:\cygwin\bin\bash.exe" "--login -c 'chmod 644 $dst"
} else {
    Write-Output "C:\code\.ci\vagrant\files\authorized_keys does not exist"
}

Run "net.exe" "start sshd"
