%WITH_COMPILER% %PYTHON%\Scripts\pip.exe install wheel . --quiet --upgrade || EXIT 1
%WITH_COMPILER% %PYTHON%\python.exe setup.py sdist bdist_wheel bdist_msi --quiet || EXIT 1
