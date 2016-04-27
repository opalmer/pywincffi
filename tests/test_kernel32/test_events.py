from pywincffi.dev.testutil import TestCase
from pywincffi.core import dist
from pywincffi.kernel32 import CloseHandle, CreateEvent, OpenEvent


class TestCreateEvent(TestCase):
    """
    Tests for :func:`pywincffi.kernel32.CreateEvent`
    """
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

    def test_can_retrieve_named_event(self):
        ffi, library = dist.load()
        name = "Global\\pywincffi-%s" % self.random_string(5)
        handle = CreateEvent(False, False, lpName=name)
        self.addCleanup(CloseHandle, handle)
        opened_event = OpenEvent(library.EVENT_ALL_ACCESS, True, name)
        self.addCleanup(CloseHandle, opened_event)
