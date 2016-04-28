#include <io.h>
#include <windows.h>

// Extra constants which are not defined in all versions of Windows or
// that pywincffi creates.
static const int FILE_FLAG_SESSION_AWARE = 0x00800000;
static const int STARTF_UNTRUSTEDSOURCE = 0x00008000;

HANDLE handle_from_fd(int fd) {
    return (HANDLE)_get_osfhandle(fd);
}
