#include <io.h>
#include <winsock2.h>
#include <winerror.h>
#include <TlHelp32.h>
#include <windows.h>

// Extra constants which are not defined in all versions of the Windows
// SDK.  If cffi fails to find the value, it ends up being picked up from
// here.
#if !defined(FILE_FLAG_SESSION_AWARE)
    static const int FILE_FLAG_SESSION_AWARE = 0x00800000;
#endif

#if !defined(STARTF_UNTRUSTEDSOURCE)
    static const int STARTF_UNTRUSTEDSOURCE = 0x00008000;
#endif

#if !defined(STARTF_PREVENTPINNING)
    static const int STARTF_PREVENTPINNING = 0x00002000;
#endif

#if !defined(STARTF_TITLEISAPPID)
    static const int STARTF_TITLEISAPPID = 0x00001000;
#endif

#if !defined(STARTF_TITLEISLINKNAME)
    static const int STARTF_TITLEISLINKNAME = 0x00000800;
#endif

HANDLE handle_from_fd(int fd) {
    return (HANDLE)_get_osfhandle(fd);
}

// Checks to see if a given event is considered invalid.  We perform this
// check in C because cffi itself has trouble creating a usable value for
// WSA_INVALID_EVENT.
BOOL wsa_invalid_event(WSAEVENT event) {
    return event == WSA_INVALID_EVENT;
}
