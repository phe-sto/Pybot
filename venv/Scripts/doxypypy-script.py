#!C:\Users\Chrichri\Auto\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'doxypypy==0.8.8.6','console_scripts','doxypypy'
__requires__ = 'doxypypy==0.8.8.6'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('doxypypy==0.8.8.6', 'console_scripts', 'doxypypy')()
    )
