from pywincffi.core.checks import input_check
from pywincffi.dev.testutil import TestCase
from pywincffi.exceptions import InputError


class TestInputCheck(TestCase):
    """
    Tests for :func:`pywincffi.core.types.input_check`
    """
    def test_valid_allowed_values(self):
        input_check("", 1, allowed_values=(1,))

    def test_valid_allowed_types(self):
        input_check("", 1, allowed_types=(int,))
        input_check("", 1, allowed_types=int)

    def test_invalid_allowed_values(self):
        for value in (1, 1.5, "", set(), {"A": "B"}):
            with self.assertRaises(TypeError):
                input_check("", None, allowed_values=value)

    def test_invalid_allowed_types(self):
        with self.assertRaises(InputError):
            input_check("", 1, allowed_types=(str, ))
