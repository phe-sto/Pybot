@echo off
cls
set function=%1
set arg1=%2
set arg2=%3
set ACTIVATE=venv/Scripts/activate
set FOLDER_PYBOT=Pybot
set FOLDER_SCRIPT=script
call %ACTIVATE%
if "%function%"=="" (
    echo Please provide a function to execute as first argument
)
if "%function%"=="clear" (
    virtualenv venv --clear
)
if "%function%"=="remove" (
    rmdir venv /s /q
)
if "%function%"=="setup" (
    virtualenv venv
    call :setup
)
if "%function%"=="export" (
    if "%arg2%"=="" (
        echo Please provide the sikuli project to export as second argument
    ) else (
        if "%arg1%"=="script" (
            python export_sikuli_script.py %arg2%
            python %FOLDER_SCRIPT%/2to3.py -w %FOLDER_PYBOT%/%arg2%.py
            isort %FOLDER_PYBOT%/%arg2%.py
            autopep8 --in-place %FOLDER_PYBOT%/%arg2%.py
            call :setup
        ) else if "%arg1%"=="class" (
                python export_sikuli_class.py %arg2%
                python %FOLDER_SCRIPT%/2to3.py -w %FOLDER_PYBOT%/%arg2%.py
                isort %FOLDER_PYBOT%/%arg2%.py
                autopep8 --in-place %FOLDER_PYBOT%/%arg2%.py
                call :setup
            ) else (
                echo Please provide specify class or script as second argument
        )
    )
)
if "%function%"=="test" (
    python %FOLDER_PYBOT%/Pybot.py
)
pause
exit /B 0
:setup
    python setup.py build
    python setup.py bdist_wheel
    pip uninstall --yes Pybot
    pip install dist/Pybot-0.1.0-py3-none-any.whl --upgrade