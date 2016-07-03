///////////////////////
// Processes
///////////////////////

// https://msdn.microsoft.com/en-us/ms684320
HANDLE WINAPI OpenProcess(
  _In_ DWORD dwDesiredAccess,
  _In_ BOOL  bInheritHandle,
  _In_ DWORD dwProcessId
);

// https://msdn.microsoft.com/en-us/ms683189
BOOL WINAPI GetExitCodeProcess(
  _In_  HANDLE  hProcess,
  _Out_ LPDWORD lpExitCode
);

// https://msdn.microsoft.com/en-us/ms683179
HANDLE WINAPI GetCurrentProcess(void);


// https://msdn.microsoft.com/en-us/ms683215
DWORD WINAPI GetProcessId(
  _In_ HANDLE Process
);

// https://msdn.microsoft.com/en-us/ms686714
BOOL WINAPI TerminateProcess(
  _In_ HANDLE hProcess,
  _In_ UINT   uExitCode
);

// https://msdn.microsoft.com/en-us/ms682489
HANDLE WINAPI CreateToolhelp32Snapshot(
  _In_ DWORD dwFlags,
  _In_ DWORD th32ProcessID
);


///////////////////////
// Pipes
///////////////////////

// https://msdn.microsoft.com/en-us/aa365152
BOOL WINAPI CreatePipe(
  _Out_    PHANDLE               hReadPipe,
  _Out_    PHANDLE               hWritePipe,
  _In_opt_ LPSECURITY_ATTRIBUTES lpPipeAttributes,
  _In_     DWORD                 nSize
);

// https://msdn.microsoft.com/en-us/aa365779
BOOL WINAPI PeekNamedPipe(
  _In_      HANDLE  hNamedPipe,
  _Out_opt_ LPVOID  lpBuffer,
  _In_      DWORD   nBufferSize,
  _Out_opt_ LPDWORD lpBytesRead,
  _Out_opt_ LPDWORD lpTotalBytesAvail,
  _Out_opt_ LPDWORD lpBytesLeftThisMessage
);

// https://msdn.microsoft.com/en-us/aa365787
BOOL WINAPI SetNamedPipeHandleState(
  _In_     HANDLE  hNamedPipe,
  _In_opt_ LPDWORD lpMode,
  _In_opt_ LPDWORD lpMaxCollectionCount,
  _In_opt_ LPDWORD lpCollectDataTimeout
);


///////////////////////
// Files
///////////////////////

// https://msdn.microsoft.com/en-us/aa363858
HANDLE WINAPI CreateFile(
  _In_     LPCTSTR               lpFileName,
  _In_     DWORD                 dwDesiredAccess,
  _In_     DWORD                 dwShareMode,
  _In_opt_ LPSECURITY_ATTRIBUTES lpSecurityAttributes,
  _In_     DWORD                 dwCreationDisposition,
  _In_     DWORD                 dwFlagsAndAttributes,
  _In_opt_ HANDLE                hTemplateFile
);

// https://msdn.microsoft.com/en-us/aa365747
BOOL WINAPI WriteFile(
  _In_        HANDLE       hFile,
  _In_        LPCVOID      lpBuffer,
  _In_        DWORD        nNumberOfBytesToWrite,
  _Out_opt_   LPDWORD      lpNumberOfBytesWritten,
  _Inout_opt_ LPOVERLAPPED lpOverlapped
);

// https://msdn.microsoft.com/en-us/aa364439
BOOL WINAPI FlushFileBuffers(
  _In_ HANDLE hFile
);

// https://msdn.microsoft.com/en-us/aa365467
BOOL WINAPI ReadFile(
  _In_        HANDLE       hFile,
  _Out_       LPVOID       lpBuffer,
  _In_        DWORD        nNumberOfBytesToRead,
  _Out_opt_   LPDWORD      lpNumberOfBytesRead,
  _Inout_opt_ LPOVERLAPPED lpOverlapped
);

// https://msdn.microsoft.com/en-us/aa365240
BOOL WINAPI MoveFileEx(
  _In_     LPCTSTR lpExistingFileName,
  _In_opt_ LPCTSTR lpNewFileName,
  _In_     DWORD   dwFlags
);

// https://msdn.microsoft.com/en-us/aa365203
BOOL WINAPI LockFileEx(
  _In_       HANDLE       hFile,
  _In_       DWORD        dwFlags,
  _Reserved_ DWORD        dwReserved,
  _In_       DWORD        nNumberOfBytesToLockLow,
  _In_       DWORD        nNumberOfBytesToLockHigh,
  _Inout_    LPOVERLAPPED lpOverlapped
);

// https://msdn.microsoft.com/en-us/aa365716
BOOL WINAPI UnlockFileEx(
  _In_       HANDLE       hFile,
  _Reserved_ DWORD        dwReserved,
  _In_       DWORD        nNumberOfBytesToUnlockLow,
  _In_       DWORD        nNumberOfBytesToUnlockHigh,
  _Inout_    LPOVERLAPPED lpOverlapped
);

///////////////////////
// Files
///////////////////////

// https://msdn.microsoft.com/en-us/ms724211
BOOL WINAPI CloseHandle(
  _In_ HANDLE hObject
);

// https://msdn.microsoft.com/en-us/ms683231
HANDLE WINAPI GetStdHandle(
  _In_ DWORD nStdHandle
);

// https://msdn.microsoft.com/en-us/ms687032
DWORD WINAPI WaitForSingleObject(
  _In_ HANDLE hHandle,
  _In_ DWORD  dwMilliseconds
);

// https://msdn.microsoft.com/en-us/ms724329
BOOL WINAPI GetHandleInformation(
  _In_  HANDLE  hObject,
  _Out_ LPDWORD lpdwFlags
);

// https://msdn.microsoft.com/en-us/ms724935
BOOL WINAPI SetHandleInformation(
  _In_ HANDLE hObject,
  _In_ DWORD  dwMask,
  _In_ DWORD  dwFlags
);

// https://msdn.microsoft.com/en-us/ms724251
BOOL WINAPI DuplicateHandle(
  _In_  HANDLE   hSourceProcessHandle,
  _In_  HANDLE   hSourceHandle,
  _In_  HANDLE   hTargetProcessHandle,
  _Out_ LPHANDLE lpTargetHandle,
  _In_  DWORD    dwDesiredAccess,
  _In_  BOOL     bInheritHandle,
  _In_  DWORD    dwOptions
);

// https://msdn.microsoft.com/en-us/ms684242
DWORD WINAPI MsgWaitForMultipleObjects(
  _In_       DWORD  nCount,
  _In_ const HANDLE *pHandles,
  _In_       BOOL   bWaitAll,
  _In_       DWORD  dwMilliseconds,
  _In_       DWORD  dwWakeMask
);


///////////////////////
// Events
///////////////////////

// https://msdn.microsoft.com/en-us/ms682396
HANDLE WINAPI CreateEvent(
  _In_opt_ LPSECURITY_ATTRIBUTES lpEventAttributes,
  _In_     BOOL                  bManualReset,
  _In_     BOOL                  bInitialState,
  _In_opt_ LPCTSTR               lpName
);

// https://msdn.microsoft.com/en-us/ms684305
HANDLE WINAPI OpenEvent(
  _In_ DWORD   dwDesiredAccess,
  _In_ BOOL    bInheritHandle,
  _In_ LPCTSTR lpName
);

// https://msdn.microsoft.com/en-us/ms685081
BOOL WINAPI ResetEvent(
  _In_ HANDLE hEvent
);


///////////////////////
// Communications
///////////////////////

// https://msdn.microsoft.com/en-us/ms737582
int closesocket(
  _In_ SOCKET s
);

// https://msdn.microsoft.com/en-us/aa363180
BOOL WINAPI ClearCommError(
  _In_      HANDLE    hFile,
  _Out_opt_ LPDWORD   lpErrors,
  _Out_opt_ LPCOMSTAT lpStat
);

// https://msdn.microsoft.com/en-us/ms741576
int WSAEventSelect(
  _In_ SOCKET   s,
  _In_ WSAEVENT hEventObject,
  _In_ long     lNetworkEvents
);

// https://msdn.microsoft.com/en-us/ms741580
int WSAGetLastError(void);

// https://msdn.microsoft.com/en-us/ms741561
WSAEVENT WSACreateEvent(void);

// https://msdn.microsoft.com/en-us/ms741572
int WSAEnumNetworkEvents(
  _In_  SOCKET             s,
  _In_  WSAEVENT           hEventObject,
  _Out_ LPWSANETWORKEVENTS lpNetworkEvents
);

///////////////////////
// Utility Functions
///////////////////////
HANDLE handle_from_fd(int);
BOOL wsa_invalid_event(WSAEVENT);
