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
