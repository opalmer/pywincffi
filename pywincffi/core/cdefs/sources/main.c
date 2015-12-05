#include <io.h>
#include <windows.h>

HANDLE handle_from_fd(int fd) {
    return (HANDLE)_get_osfhandle(fd);
}
