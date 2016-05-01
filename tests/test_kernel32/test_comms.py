from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.kernel32 import CreateFile, ClearCommError, CloseHandle
from pywincffi.exceptions import WindowsAPIError


class TestClearCommError(TestCase):
    def test_clear_error(self):
        ffi, library = dist.load()

        # Try to find a COM device, skip the test if we can't
        # find one.  The 'maximum' comes from here:
        #   https://support.microsoft.com/en-us/kb/100111
        found_com_device = False
        for i in range(256):
            try:
                handle = CreateFile(
                    "\\\\.\\COM%d" % i,
                    library.GENERIC_READ | library.GENERIC_WRITE,
                    dwCreationDisposition=library.OPEN_EXISTING,
                    dwShareMode=0
                )
                found_com_device = True
                self.addCleanup(CloseHandle, handle)
                ClearCommError(handle)
                break
            except WindowsAPIError:
                code, _ = ffi.getwinerror()
                if code != library.ERROR_FILE_NOT_FOUND:
                    self.fail("Unexpected Windows API error: %s" % code)

        if not found_com_device:
            self.skipTest("No COM devices present.")
