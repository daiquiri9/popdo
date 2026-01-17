@echo off
echo Building PopDo...

if not exist venv (
    echo venv not found, assuming packages installed globally or in active env.
)

REM Clean previous build
rd /s /q build
rd /s /q dist
del /q PopDo.spec

REM Run PyInstaller
REM --noconsole: Don't show terminal window
REM --onefile: Bundle everything into one exe
REM --name: Output name
REM --hidden-import: Ensure pynput backends are found
REM --collect-all: sometimes needed for customtkinter to find its assets
pyinstaller --noconsole --onefile ^
    --name PopDo ^
    --hidden-import=pynput.keyboard._win32 ^
    --hidden-import=pynput.mouse._win32 ^
    --collect-all customtkinter ^
    src/main.py

echo.
echo Build complete! Check the 'dist' folder for PopDo.exe.
pause
