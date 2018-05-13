@echo off
call venv/Scripts/activate
cls
isort {0}
autopep8 --in-place --agressive {0}
python venv\Tools\scripts\2to3.py {0}
pause