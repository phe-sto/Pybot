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
    if "%arg2%"=="" (
        echo Please provide the sikuli project to export as second argument
    ) else (
        if "%arg1%"=="class" (
            python export_sikuli_class.py %arg2%
            python venv/Tools/scripts/2to3.py -w Pybot/%arg2%.py
            isort Pybot/%arg2%.py
            autopep8 --in-place Pybot/%arg2%.py
            call :setup
        ) else (
            echo Please provide specify class or script as second argument
        )
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