
//
// NOTE: The tests for this file, tests/test_core/test_cdefs/test_structs.py
//       depend on a struct's names to follow this format:
//           } NAME, NAME, NAME;
//

// https://msdn.microsoft.com/en-us/library/aa379560
typedef struct _SECURITY_ATTRIBUTES {
    DWORD  nLength;
    LPVOID lpSecurityDescriptor;
    BOOL   bInheritHandle;
} SECURITY_ATTRIBUTES, *PSECURITY_ATTRIBUTES, *LPSECURITY_ATTRIBUTES;

// https://msdn.microsoft.com/en-us/library/ms684342
typedef struct _OVERLAPPED {
  ULONG_PTR Internal;
  ULONG_PTR InternalHigh;
  union {
    struct {
      DWORD Offset;
      DWORD OffsetHigh;
    };
    PVOID  Pointer;
  };
  HANDLE    hEvent;
} OVERLAPPED, *LPOVERLAPPED;

// https://msdn.microsoft.com/en-us/library/ms724284
typedef struct _FILETIME {
  DWORD dwLowDateTime;
  DWORD dwHighDateTime;
} FILETIME, *PFILETIME;

// https://msdn.microsoft.com/en-us/library/ms686331
typedef struct _STARTUPINFO {
  DWORD  cb;
  LPTSTR lpReserved;
  LPTSTR lpDesktop;
  LPTSTR lpTitle;
  DWORD  dwX;
  DWORD  dwY;
  DWORD  dwXSize;
  DWORD  dwYSize;
  DWORD  dwXCountChars;
  DWORD  dwYCountChars;
  DWORD  dwFillAttribute;
  DWORD  dwFlags;
  WORD   wShowWindow;
  WORD   cbReserved2;
  LPBYTE lpReserved2;
  HANDLE hStdInput;
  HANDLE hStdOutput;
  HANDLE hStdError;
} STARTUPINFO, *LPSTARTUPINFO;

// https://msdn.microsoft.com/en-us/library/aa363200
typedef struct _COMSTAT {
  DWORD fCtsHold  :1;
  DWORD fDsrHold  :1;
  DWORD fRlsdHold  :1;
  DWORD fXoffHold  :1;
  DWORD fXoffSent  :1;
  DWORD fEof  :1;
  DWORD fTxim  :1;
  DWORD fReserved  :25;
  DWORD cbInQue;
  DWORD cbOutQue;
} COMSTAT, *LPCOMSTAT;

// https://msdn.microsoft.com/en-us/ms741653
typedef struct _WSANETWORKEVENTS {
  long lNetworkEvents;
  int  iErrorCode[...];
} WSANETWORKEVENTS, *LPWSANETWORKEVENTS;
