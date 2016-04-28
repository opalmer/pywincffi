import sys
import time

from mock import patch

from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import WindowsAPIError, InputError
from pywincffi.kernel32 import events  # used by mocks
from pywincffi.kernel32 import (
    CloseHandle, CreateEvent, OpenEvent, ResetEvent, WaitForSingleObject)


# These tests cause TestPidExists to fail under Python 3.4 so for now
# we skip these tests.  Because we're only testing CreateEvent, and
# TestPidExists worked before TestCreateEvent exists, we'll skip these
# for now.
#  Traceback (most recent call last):
# [...]
#    File "c:\python34\lib\subprocess.py", line 754, in __init__
#      _cleanup()
#    File "c:\python34\lib\subprocess.py", line 474, in _cleanup
#      res = inst._internal_poll(_deadstate=sys.maxsize)
#    File "c:\python34\lib\subprocess.py", line 1147, in _internal_poll
#      if _WaitForSingleObject(self._handle, 0) == _WAIT_OBJECT_0:
#  OSError: [WinError 6] The handle is invalid
# TODO: Need to figure out why this happens ^^^
class TestCreateEvent(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.CreateEvent`
    """
    def setUp(self):
        super(TestCreateEvent, self).setUp()
        if sys.version_info[0:2] == (3, 4):
            self.skipTest("Not compatible with Python 3.4")

    def test_create_event_valid_handle(self):
        handle = CreateEvent(False, False)
        CloseHandle(handle)  # will raise exception if the handle is invalid

    def test_creating_duplicate_event_does_not_raise_error(self):
        # Windows raises set the last error to ERROR_ALREADY_EXISTS
        # if an event object with the same name already exists.  The
        # pywincffi API ignores this error and returns the handle
        # object.
        name = "pywincffi-%s" % self.random_string(5)
        handle1 = CreateEvent(False, False, lpName=name)
        self.addCleanup(CloseHandle, handle1)
        handle2 = CreateEvent(False, False, lpName=name)
        self.addCleanup(CloseHandle, handle2)

    def test_raises_non_error_already_exists(self):
        def raise_(*_):
            raise WindowsAPIError("CreateEvent", "", -1)

        with patch.object(events, "error_check", side_effect=raise_):
            with self.assertRaises(WindowsAPIError):
                CreateEvent(False, False)

    def test_can_retrieve_named_event(self):
        _, library = dist.load()
        name = "pywincffi-%s" % self.random_string(5)
        handle = CreateEvent(False, False, lpName=name)
        self.addCleanup(CloseHandle, handle)
        opened_event = OpenEvent(library.EVENT_ALL_ACCESS, True, name)
        self.addCleanup(CloseHandle, opened_event)

    def test_check_lpeventattributes_type(self):
        with self.assertRaises(InputError):
            CreateEvent(False, False, lpEventAttributes="")


class TestResetEvent(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.ResetEvent`
    """
    def test_basic_reset(self):
        handle = CreateEvent(True, True)
        self.addCleanup(CloseHandle, handle)
        ResetEvent(handle)

    def test_resets_event(self):
        handle = CreateEvent(True, True)
        self.addCleanup(CloseHandle, handle)
        ResetEvent(handle)

        # If the event is not in a signaled state,
        # because ResetEvent was called, then it should
        # take >= 1 second to reset the assert statement.
        start = time.time()
        WaitForSingleObject(handle, 1000)
        self.assertGreaterEqual(time.time() - start, 1)
