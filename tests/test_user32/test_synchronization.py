from pywincffi.core import dist
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import InputError, WindowsAPIError
from pywincffi.kernel32 import CreateEvent, CloseHandle
from pywincffi.user32 import MsgWaitForMultipleObjects


class TestMsgWaitForMultipleObjects(TestCase):
    """
    Tests for :func:`pywincffi.user32.WaitForSingleObject`
    """
    def test_timeout(self):
        _, library = dist.load()
        e1 = CreateEvent(True, False)
        self.addCleanup(CloseHandle, e1)
        e2 = CreateEvent(True, False)
        self.addCleanup(CloseHandle, e2)
        result = MsgWaitForMultipleObjects(
            [e1, e2], False, 0, library.QS_ALLEVENTS)
        self.assertEqual(result, library.WAIT_TIMEOUT)

    def test_triggered(self):
        _, library = dist.load()
        e1 = CreateEvent(True, False)
        self.addCleanup(CloseHandle, e1)
        e2 = CreateEvent(True, True)
        self.addCleanup(CloseHandle, e2)

        # The result here should be 1 because the e2
        # event is triggered by e1 is not.
        result = MsgWaitForMultipleObjects(
            [e1, e2], False, 0, library.QS_ALLEVENTS)
        self.assertEqual(result, 1)

    def test_type_check_on_pHandles_input_not_list(self):
        _, library = dist.load()
        e1 = CreateEvent(True, False)
        self.addCleanup(CloseHandle, e1)

        with self.assertRaises(InputError):
            MsgWaitForMultipleObjects(e1, False, 0, library.QS_ALLEVENTS)

    def test_type_check_on_pHandles_value_not_handle(self):
        _, library = dist.load()

        with self.assertRaises(InputError):
            MsgWaitForMultipleObjects([""], False, 0, library.QS_ALLEVENTS)

    def test_wait_failed(self):
        _, library = dist.load()

        events = []
        for _ in range(library.MAXIMUM_WAIT_OBJECTS + 1):
            event = CreateEvent(True, False)
            self.addCleanup(CloseHandle, event)
            events.append(event)

        with self.assertRaises(WindowsAPIError) as error:
            MsgWaitForMultipleObjects(events, False, 0, library.QS_ALLEVENTS)

        # The maximum number of events that MsgWaitForMultipleObjects can
        # wait on is MAXIMUM_WAIT_OBJECTS - 1.  Anything else should cause
        # ERROR_INVALID_PARAMETER to be raised via WindowsAPIError.
        self.assertEqual(
            error.exception.errno, library.ERROR_INVALID_PARAMETER)
