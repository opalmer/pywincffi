import re
from os.path import isfile, join

from pywincffi.core.ffi import Library
from pywincffi.core.testutil import TestCase


# TODO: it would be better if we had a parser to parse the header
class TestFunctionsHeader(TestCase):
    def test_file_exists(self):
        for path in Library.HEADERS:
            if path.endswith("functions.h"):
                self.assertTrue(isfile(path))
                break
        else:
            self.fail("Failed to locate header in Library.HEADERS")

    def get_header_functions(self):
        with open(join(Library.HEADERS_ROOT, "functions.h"), "r") as header:
            for line in header:
                line = line.strip()
                if not line or line.startswith("//"):
                    continue

                match = re.match("^[A-Z]* ([A-Za-z]*)\(.*\);$", line)
                if match is not None:
                    yield match.group(1)

    def test_library_has_attributes_defined_in_header(self):
        ffi, library = Library.load()

        for function_name in self.get_header_functions():
            self.assertTrue(hasattr(library, function_name))

    def test_library_has_functions_defined_in_header(self):
        ffi, library = Library.load()

        for function_name in self.get_header_functions():
            function = getattr(library, function_name)
            self.assertTrue(callable(function))

