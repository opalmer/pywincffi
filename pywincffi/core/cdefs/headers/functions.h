//
// NOTE: The tests for this file, tests/test_core/test_cdefs/test_functions.py
//       depend on a function's format to be the following:
//           RETURN_TYPE FunctionName(...
//

// Custom functions
VOID SetLastError(DWORD);

// Processes
HANDLE OpenProcess(DWORD, BOOL, DWORD);
BOOL GetExitCodeProcess(HANDLE, LPDWORD);
HANDLE GetCurrentProcess();
DWORD GetProcessId(HANDLE);

// Pipes
BOOL CreatePipe(PHANDLE, PHANDLE, LPSECURITY_ATTRIBUTES, DWORD);
BOOL PeekNamedPipe(HANDLE, LPVOID, DWORD, LPDWORD, LPDWORD, LPDWORD);
BOOL SetNamedPipeHandleState(HANDLE, LPDWORD, LPDWORD, LPDWORD);

// Files
HANDLE CreateFile(
    LPCTSTR, DWORD, DWORD, LPSECURITY_ATTRIBUTES, DWORD, DWORD, HANDLE);
BOOL WriteFile(HANDLE, LPCVOID, DWORD, LPDWORD, LPOVERLAPPED);
BOOL FlushFileBuffers(HANDLE);
BOOL ReadFile(HANDLE, LPVOID, DWORD, LPDWORD, LPOVERLAPPED);
BOOL MoveFileEx(LPCTSTR, LPCTSTR, DWORD);
BOOL LockFileEx(HANDLE, DWORD, DWORD, DWORD, DWORD, LPOVERLAPPED);
BOOL UnlockFileEx(HANDLE, DWORD, DWORD, DWORD, LPOVERLAPPED);

// Handles
HANDLE handle_from_fd(int);
BOOL CloseHandle(HANDLE);
HANDLE GetStdHandle(DWORD);
DWORD WaitForSingleObject(HANDLE, DWORD);
BOOL GetHandleInformation(HANDLE, LPDWORD);
BOOL SetHandleInformation(HANDLE, DWORD, DWORD);
