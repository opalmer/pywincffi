%PYTHON%\Scripts\pycodestyle.exe C:\project\pywincffi C:\project\tests || EXIT 1

SET DISABLED_PYWINCFFI_CHECKS=""
SET DISABLED_TEST_CHECKS=missing-docstring,invalid-name,too-many-arguments,protected-access,no-self-use,unused-argument,too-few-public-methods

%PYTHON%\Scripts\pylint.exe C:\project\pywincffi --reports no --disable %DISABLED_PYWINCFFI_CHECKS% || EXIT 1
%PYTHON%\Scripts\pylint.exe C:\project\tests --reports no --disable %DISABLED_TEST_CHECKS% || EXIT 1
