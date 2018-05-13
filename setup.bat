@echo off
call venv/Scripts/activate
cls
python setup.py bdist_wheel
pip uninstall --yes Pybot
pip install dist/Pybot-0.1.0-py3-none-any.whl --upgrade
pause