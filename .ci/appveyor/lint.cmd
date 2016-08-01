%PYTHON%\Scripts\pep8.exe C:\project\pywincffi C:\project\tests || EXIT 1

SET DISABLED_PYWINCFFI_CHECKS=""
SET DISABLED_TEST_CHECKS=missing-docstring,invalid-name,too-many-arguments,protected-access,no-self-use,unused-argument,too-few-public-methods
IF "%PYTHON_VERSION%" == "2.6.x" SET DISABLED_PYWINCFFI_CHECKS=bad-option-value,unpacking-non-sequence,maybe-no-member,star-args
IF "%PYTHON_VERSION%" == "2.6.x" SET DISABLED_TEST_CHECKS=missing-docstring,invalid-name,too-many-arguments,protected-access,no-self-use,unused-argument,maybe-no-member,too-few-public-methods,too-many-public-methods,unpacking-non-sequence,bad-option-value,star-args,no-member,import-error

%PYTHON%\Scripts\pylint.exe C:\project\pywincffi --reports no --disable %DISABLED_PYWINCFFI_CHECKS% || EXIT 1
%PYTHON%\Scripts\pylint.exe C:\project\tests --reports no --disable %DISABLED_TEST_CHECKS% || EXIT 1
