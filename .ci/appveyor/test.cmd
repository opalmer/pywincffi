%WITH_COMPILER% %PYTHON%\Scripts\pip.exe install -r dev_requirements.txt --upgrade --quiet || EXIT 1
%WITH_COMPILER% %PYTHON%\Scripts\py.test.exe --strict --verbose --cov pywincffi || EXIT 1
%PYTHON%\Scripts\coverage.exe xml || EXIT 1
%PYTHON%\Scripts\codecov.exe --required || EXIT 1
