. "C:\code\.ci\vagrant\functions.ps1"

RunScript "C:\code\.ci\vagrant\provision\system.ps1"
RunScript "C:\code\.ci\vagrant\provision\download.ps1"
RunScript "C:\code\.ci\vagrant\provision\visual-studio.ps1"
RunScript "C:\code\.ci\vagrant\provision\cygwin.ps1"
RunScript "C:\code\.ci\vagrant\provision\sshd.ps1"
RunScript "C:\code\.ci\vagrant\provision\python.ps1"

