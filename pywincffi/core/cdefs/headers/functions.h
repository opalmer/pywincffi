//
// NOTE: The tests for this file, tests/test_core/test_cdefs/test_functions.py
//       depend on a function's format to be the following:
//           RETURN_TYPE FunctionName(...
//


// Processes
HANDLE OpenProcess(DWORD, BOOL, DWORD);

// Files
BOOL CreatePipe(PHANDLE, PHANDLE, LPSECURITY_ATTRIBUTES, DWORD);
BOOL CloseHandle(HANDLE);
BOOL WriteFile(HANDLE, LPCVOID, DWORD, LPDWORD, LPOVERLAPPED);
BOOL ReadFile(HANDLE, LPVOID, DWORD, LPDWORD, LPOVERLAPPED);
