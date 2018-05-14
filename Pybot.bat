@echo off
cls
set function=%1
set arg1=%2
set arg2=%3
call venv/Scripts/activate
if "%function%"=="" (
    echo Please provide a function to execute as first argument
)
if "%function%"=="setup" (
    call :setup
)
if "%function%"=="export" (
    if "%arg1%"=="" (
        echo Please provide the sikuli project to export as second argument
    ) else (
        python export_sikuli_class.py %arg1%
        isort Pybot/%arg1%.py
        autopep8 --in-place Pybot/%arg1%.py
        python venv/Tools/scripts/2to3.py -w Pybot/%arg1%.py
        call :setup
    )
)
if "%function%"=="test" (
    python Pybot/Pybot.py
)
pause
exit /B 0
:setup
    python setup.py bdist_wheel
    pip uninstall --yes Pybot
    pip install dist/Pybot-0.1.0-py3-none-any.whl --upgrade