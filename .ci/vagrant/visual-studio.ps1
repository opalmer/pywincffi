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

# ISOs must be mounted from the local machine
if (!(Test-Path -Path C:\Users\vagrant\VS2008ExpressENUX1397868.iso )) {
    Write-Output "Creating local copy of VS2008ExpressENUX1397868.iso"
    Copy-Item C:\provision\visual_studio\VS2008ExpressENUX1397868.iso C:\Users\vagrant\VS2008ExpressENUX1397868.iso
} else {
    Write-Output "(skipped) Creating local copy of VS2008ExpressENUX1397868.iso"
}

MountISO "C:\Users\vagrant\VS2008ExpressENUX1397868.iso"

# return statements in functions don't function like you'd expect so
# we use Get-DiskImage here instead of asking for a result from MountISO
$drive = $(Get-DiskImage "C:\Users\vagrant\VS2008ExpressENUX1397868.iso").DriveLetter

# ISOs must be mounted from the local machine
if (!(Test-Path -Path C:\Users\vagrant\VS2010Express1.iso )) {
    Write-Output "Creating local copy of VS2010Express1.iso"
    Copy-Item C:\provision\visual_studio\VS2010Express1.iso C:\Users\vagrant\VS2010Express1.iso
} else {
    Write-Output "(skipped) Creating local copy of VS2010Express1.iso"
}

MountISO "C:\Users\vagrant\VS2010Express1.iso"

# return statements in functions don't function like you'd expect so
# we use Get-DiskImage here instead of asking for a result from MountISO
$drive = $(Get-DiskImage "C:\Users\vagrant\VS2010Express1.iso").DriveLetter


