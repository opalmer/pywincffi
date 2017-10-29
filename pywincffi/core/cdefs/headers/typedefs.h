//
// This file contains type definitions that are required by other
// headers.  In a normal C environment these would come directly
// from the system headers.  With cffi however it has a set defined
// types:
//      https://bitbucket.org/cffi/cffi/raw/default/c/commontypes.c
//
// Any additional types we need must be defined here.  This file must
// loaded before any other headers are in dist.py.
//

typedef int... SOCKET;
typedef HANDLE WSAEVENT;  // according to winsock2.h

// https://docs.microsoft.com/en-us/windows/console/coord-str
typedef struct _COORD {
  SHORT X;
  SHORT Y;
} COORD, *PCOORD;

// https://docs.microsoft.com/en-us/windows/console/small-rect-str
typedef struct _SMALL_RECT {
  SHORT Left;
  SHORT Top;
  SHORT Right;
  SHORT Bottom;
} SMALL_RECT;

typedef struct _CHAR_INFO {
  union {
    WCHAR UnicodeChar;
    CHAR  AsciiChar;
  } Char;
  WORD  Attributes;
} CHAR_INFO, *PCHAR_INFO;
