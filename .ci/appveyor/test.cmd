SET REQUIREMENTS=dev_requirements.txt --upgrade
IF "%PYTHON_VERSION%" == "2.6.x" SET REQUIREMENTS=dev_requirements-2.6.txt
%WITH_COMPILER% %PYTHON%\Scripts\pip.exe install -r %REQUIREMENTS% --quiet || EXIT 1
%WITH_COMPILER% %PYTHON%\Scripts\py.test.exe --strict --verbose --cov pywincffi || EXIT 1
%PYTHON%\Scripts\coverage.exe xml || EXIT 1
%PYTHON%\Scripts\codecov.exe --required || EXIT 1
