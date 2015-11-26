. "c:\provision\scripts\functions.ps1"

Download http://download.microsoft.com/download/8/B/5/8B5804AD-4990-40D0-A6AA-CE894CBBB3DC/VS2008ExpressENUX1397868.iso C:\provision\visual_studio\VS2008ExpressENUX1397868.iso
Download http://download.microsoft.com/download/1/E/5/1E5F1C0A-0D5B-426A-A603-1798B951DDAE/VS2010Express1.iso C:\provision\visual_studio\VS2010Express1.iso

$vs2010mount = Mount-DiskImage C:\provision\visual_studio\VS2010Express1.iso -PassThrough
$vs2010drive = $($vs2010mount | Get-Volume).DriveLetter
$vs2008mount = Mount-DiskImage C:\provision\visual_studio\VS2008ExpressENUX1397868.iso -PassThrough
$vs2008drive = $($vs2008mount | Get-Volume).DriveLetter
