@ECHO ON

:: A simple script for testing on Windows.  This does almost the same thing
:: that Travis and AppVeyor do except it does not perform additional setup
:: steps such as creating a virtual environment.

pycodestyle pywincffi
IF %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

pycodestyle tests
IF %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

pylint pywincffi --reports no
IF %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

pylint tests --reports no ^
    --disable missing-docstring,invalid-name,too-many-arguments ^
    --disable protected-access,no-self-use,unused-argument ^
    --disable too-few-public-methods
IF %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

python setup.py bdist_wheel > NUL
IF %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

py.test.exe --strict --verbose --cov pywincffi
IF %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

sphinx-build -q -b html -W -E -a -d docs/build/doctrees docs/source docs/build/html
