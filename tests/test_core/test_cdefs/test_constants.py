import re
from os.path import isfile, join

from six import integer_types

from pywincffi.core import dist
from pywincffi.core.testutil import TestCase


# TODO: it would be better if we had a parser to parse the header
class TestConstantsHeader(TestCase):
    def test_file_exists(self):
        for path in dist.Distribution.HEADERS:
            if path.endswith("constants.h"):
                self.assertTrue(isfile(path))
                break
        else:
            self.fail("Failed to locate header in Library.HEADERS")

    def get_constants(self):
        for path in dist.Distribution.HEADERS:
            if path.endswith("constants.h"):
                with open(path, "r") as header:
                    for line in header:
                        line = line.strip()
                        if not line or line.startswith("//"):
                            continue

                        match = re.match("^#define ([A-Z_]*) \.\.\..*$", line)
                        if match is not None:
                            yield match.group(1)

    def test_library_has_attributes_defined_in_header(self):
        ffi, library = dist.load()

        for constant_name in self.get_constants():
            self.assertTrue(hasattr(library, constant_name))

    def test_constant_type(self):
        ffi, library = dist.load()
        valid_types = tuple(list(integer_types) + [bool])

        for constant_name in self.get_constants():
            self.assertIsInstance(getattr(library, constant_name), valid_types)
