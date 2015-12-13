import re
from os.path import isfile

from pywincffi.core import dist
from pywincffi.core.testutil import TestCase, c_file


# TODO: it would be better if we had a parser to parse the header
class TestFunctionsHeader(TestCase):
    LIBRARY_MODE = "inline"

    def test_file_exists(self):
        for path in dist.Distribution.HEADERS:
            if path.endswith("functions.h"):
                self.assertTrue(isfile(path))
                break
        else:
            self.fail("Failed to locate header in dist.Distribution.HEADERS")

    def get_header_functions(self):
        for path in dist.Distribution.HEADERS:
            if path.endswith("functions.h"):
                for line in c_file(path):
                    match = re.match(r"^[A-Z]* ([A-Za-z]*)\(.*\);$", line)
                    if match is not None:
                        yield match.group(1)

    def test_library_has_attributes_defined_in_header(self):
        _, library = dist.load()

        for function_name in self.get_header_functions():
            self.assertTrue(hasattr(library, function_name))

    def test_library_has_functions_defined_in_header(self):
        _, library = dist.load()

        for function_name in self.get_header_functions():
            function = getattr(library, function_name)
            self.assertTrue(callable(function))
