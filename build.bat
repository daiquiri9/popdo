@echo off
setlocal
echo Building PopDo (Optimized)...

REM Define build environment path
set BUILD_ENV=build_env

REM Check if build_env exists
if not exist %BUILD_ENV% (
    echo Creating virtual environment for clean build...
    python -m venv %BUILD_ENV%
)

echo Activating environment and updating requirements...
call %BUILD_ENV%\Scripts\activate.bat
pip install -r requirements.txt

REM Clean previous build
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist PopDo.spec del /q PopDo.spec

REM Run PyInstaller from the virtual environment
echo Running PyInstaller...
pyinstaller --noconsole --onefile ^
    --name PopDo ^
    --hidden-import=pynput.keyboard._win32 ^
    --hidden-import=pynput.mouse._win32 ^
    --hidden-import=PIL ^
    --collect-all pystray ^
    --collect-all customtkinter ^
    src/main.py

echo.
echo Build complete! Check 'dist/PopDo.exe'
echo Deactivating environment...
deactivate
echo Done.
pause
