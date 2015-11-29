. "C:\code\.ci\vagrant\functions.ps1"

#
# Installs the core Python packages such as setuptools,
# pip and virtualenv.
#

SafeRun "$python" "-m compileall $install_path"
SafeRun "$python" "C:\provision\python\ez_setup.py"
SafeRun "$easy_install" "pip"
SafeRun "$pip" "install virtualenv"

Download "https://bootstrap.pypa.io/ez_setup.py" "C:\provision\python\ez_setup.py"