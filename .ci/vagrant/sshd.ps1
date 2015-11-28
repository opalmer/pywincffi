. "C:\code\.ci\vagrant\functions.ps1"

# Setup sshd (needed for remote intrepreters)
$service = Get-Service -Name sshd -ErrorAction SilentlyContinue
if ($service.Length -eq 0) {
    Write-Output "Configuring sshd"
    $args = "--login -c '/bin/ssh-host-config--yes --name sshd --pwd vagrant'"
    Run "C:\cygwin\bin\bash.exe" $args
}

Run "net.exe" "start sshd"
