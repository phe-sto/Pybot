@echo off
cls
set function=%1
set arg1=%2
set arg2=%3
set ACTIVATE = "venv/Scripts/activate"
set PYBOT_FOLDER = "Pybot"
if "%function%"=="" (
    echo Please provide a function to execute as first argument
)
if "%function%"=="clear" (
    call
    virtualenv venv --clear
)
if "%function%"=="remove" (
    deactivate
    rmdir venv /s /q
)
if "%function%"=="setup" (
    deactivate
    virtualenv venv
    call %ACTIVATE%
    call :setup
)
if "%function%"=="export" (
    if "%arg2%"=="" (
        echo Please provide the sikuli project to export as second argument
    ) else (
        if "%arg1%"=="class" (
            call %ACTIVATE%
            python export_sikuli_class.py %arg2%
            python script/2to3.py -w %PYBOT_FOLDER%/%arg2%.py
            isort %PYBOT_FOLDER%/%arg2%.py
            autopep8 --in-place %PYBOT_FOLDER%/%arg2%.py
            call :setup
        ) else (
            echo Please provide specify class or script as second argument
        )
    )
)
if "%function%"=="test" (
    call %ACTIVATE%
    python %PYBOT_FOLDER%/Pybot.py
)
pause
deactivate
exit /B 0
:setup
    python setup.py build
    python setup.py bdist_wheel
    pip uninstall --yes Pybot
    pip install dist/Pybot-0.1.0-py3-none-any.whl --upgrade