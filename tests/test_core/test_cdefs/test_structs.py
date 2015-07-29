from os.path import isfile, join

from pywincffi.core.ffi import Library
from pywincffi.core.testutil import TestCase


# TODO: it would be better if we had a parser to parse the header
class TestStructsHeader(TestCase):
    def test_file_exists(self):
        for path in Library.HEADERS:
            if path.endswith("structs.h"):
                self.assertTrue(isfile(path))
                break
        else:
            self.fail("Failed to locate header in Library.HEADERS")

    def test_get_structs(self):
        with open(join(Library.HEADERS_ROOT, "structs.h"), "r") as header:
            for line in header:
                line = line.strip()
                if not line or line.startswith("//"):
                    continue

                # This is a bit hacky but it's effective...
                if line.startswith("}") and line.endswith(";"):

                    for char in ("}", ";", "*", " "):
                        line = line.replace(char, "")

                    for entry in filter(bool, line.strip().split(",")):
                        yield entry

    def test_library_has_attributes_defined_in_header(self):
        ffi, library = Library.load()
        
        for struct_name in self.test_get_structs():
            try:
                ffi.new(struct_name)

            # If the struct is not a pointer then we heed to call ffi.new
            # in a different way.  We could test to see if the name starts with
            # * but this is slightly better because it ties is less into the
            # syntax and more into the behavior of ffi.new.
            except TypeError as error:
                self.assertEqual(
                    str(error),
                    "expected a pointer or array ctype, got '%s'" % struct_name)
                ffi.new("%s[0]" % struct_name)

