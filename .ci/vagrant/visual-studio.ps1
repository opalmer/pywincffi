. "C:\code\.ci\vagrant\functions.ps1"

function MountISO {
    $iso = $args[0]
    $mount_info = $(Get-DiskImage $iso)

    if (!($mount_info.Attached)) {
        Write-Output "Mounting $iso"
        $mount = Mount-DiskImage $iso -PassThru
        $drive = $($mount | Get-Volume).DriveLetter

    } else {
        Write-Output "(skipped) Mounting $iso"
        $drive = $($mount_info | Get-Volume).DriveLetter
    }
    Write-Output "$iso is mounted at $drive"
}

function DismountISO {
    $iso = $args[0]
    $mount_info = $(Get-DiskImage $iso)

    if (($mount_info.Attached)) {
        Write-Output "Dismounting $iso"
        Dismount-DiskImage -ImagePath $iso
    }
}

function VSSetup {
    $setup = $args[0]
    $lockfile = $args[1]
    Remove-Item $lockfile

    Write-Output "==========================================================="
    Write-Output "======================= PLEASE READ ======================="
    Write-Output "==========================================================="
    Write-Output "Please follow the steps below to continue the provision "
    Write-Output "process.  The express editions of Visual Studio don't "
    Write-Output "have an easy way to perform an unattended install."
    Write-Output "  1. Locate and execute $setup."
    Write-Output "  2. Install Visual C++ Express and related components."
    Write-Output "  3. Create $lockfile when finished."
    Write-Output "==========================================================="
    Write-Output "Waiting for $lockfile to be created"
    Write-Output "==========================================================="

    while (!(Test-Path -Path $lockfile)) {
        Start-Sleep -Seconds 1
    }
}

if (!(Test-Path -Path "C:\Program Files (x86)\Microsoft Visual Studio 9.0")) {
    # ISOs must be mounted from the local machine
    if (!(Test-Path -Path C:\Users\vagrant\2012r2.iso )) {
        Write-Output "Creating local copy of 2012r2.iso"
        Copy-Item C:\provision\2012r2.iso C:\Users\vagrant\2012r2.iso
    } else {
        Write-Output "(skipped) Creating local copy of 2012r2.iso"
    }

    MountISO "C:\Users\vagrant\2012r2.iso"
    $os_drive = $(Get-DiskImage "C:\Users\vagrant\2012r2.iso" | Get-Volume).DriveLetter

    # Visual Studio 2008 requires .NET Framework 3.5 in order
    # to install.
    Write-Output "Installing .NET Framework"
    Install-WindowsFeature Net-Framework-Core -source "$os_drive`:\sources\sxs"
    DismountISO "C:\Users\vagrant\2012r2.iso"
    Remove-Item "C:\Users\vagrant\2012r2.iso" -InformationAction SilentlyContinue

    # ISOs must be mounted from the local machine
    if (!(Test-Path -Path C:\Users\vagrant\VS2008ExpressENUX1397868.iso )) {
        Write-Output "Creating local copy of VS2008ExpressENUX1397868.iso"
        Copy-Item C:\provision\visual_studio\VS2008ExpressENUX1397868.iso C:\Users\vagrant\VS2008ExpressENUX1397868.iso
    } else {
        Write-Output "(skipped) Creating local copy of VS2008ExpressENUX1397868.iso"
    }

    # Install VS
    MountISO "C:\Users\vagrant\VS2008ExpressENUX1397868.iso"
    $drive = $(Get-DiskImage "C:\Users\vagrant\VS2008ExpressENUX1397868.iso" | Get-Volume).DriveLetter
    VSSetup "$drive`:\Setup.hta" "C:\Users\vagrant\vs2008_installed.txt"
    DismountISO "C:\Users\vagrant\VS2008ExpressENUX1397868.iso"
    Remove-Item "C:\Users\vagrant\VS2008ExpressENUX1397868.iso"

    # Install redists
    Write-Output "Installing Visual Studio 2008 Redistributable (x86)"
    Run "C:\provision\vc_redist\2008x86.exe" "/qb"
    Write-Output "Installing Visual Studio 2008 Redistributable (x64)"
    Run "C:\provision\vc_redist\2008x64.exe" "/qb"

} else {
    Write-Output "VS2008 appears to already be installed"
}

if (!(Test-Path -Path "C:\Program Files (x86)\Microsoft Visual Studio 10.0")) {
    # ISOs must be mounted from the local machine
    if (!(Test-Path -Path C:\Users\vagrant\VS2010Express1.iso )) {
        Write-Output "Creating local copy of VS2010Express1.iso"
        Copy-Item C:\provision\visual_studio\VS2010Express1.iso C:\Users\vagrant\VS2010Express1.iso
    } else {
        Write-Output "(skipped) Creating local copy of VS2010Express1.iso"
    }

    # Install VS
    MountISO "C:\Users\vagrant\VS2010Express1.iso"
    $drive = $(Get-DiskImage "C:\Users\vagrant\VS2010Express1.iso" | Get-Volume).DriveLetter
    VSSetup "$drive`:\Setup.hta" "C:\Users\vagrant\vs2010_installed.txt"
    DismountISO "C:\Users\vagrant\VS2010Express1.iso"
    Remove-Item "C:\Users\vagrant\VS2010Express1.iso"

    # Install redists
    Write-Output "Installing Visual Studio 2010 Redistributable (x64)"
    Run "C:\provision\vc_redist\2010x64.exe" "/passive /norestart"
    Write-Output "Installing Visual Studio 2010 Redistributable (x86)"
    Run "C:\provision\vc_redist\2010x86.exe" "/passive /norestart"

} else {
    Write-Output "VS2010 appears to already be installed"
}
