@echo off
echo ===========================================
echo Building Windows Deep Cleaner Executable
echo ===========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)

REM Install PyInstaller if not already installed
echo Installing PyInstaller...
pip install pyinstaller --quiet

REM Build the executable
echo.
echo Building executable...
pyinstaller --onefile --windowed --name "WindowsDeepCleaner" --clean main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ===========================================
echo Build successful!
echo ===========================================
echo.
echo Executable location: dist\WindowsDeepCleaner.exe
echo.
echo You can now:
echo 1. Run the executable directly: dist\WindowsDeepCleaner.exe
echo 2. Copy it to another Windows machine
echo 3. Distribute it to users
echo.
pause
