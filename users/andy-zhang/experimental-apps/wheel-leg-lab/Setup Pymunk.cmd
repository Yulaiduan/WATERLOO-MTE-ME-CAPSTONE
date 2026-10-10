@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 python -m venv .venv
 if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
call npm ci
if errorlevel 1 goto failed
call npm run build
if errorlevel 1 goto failed
echo Setup complete. Double-click Start Motion Lab.cmd.
pause
exit /b 0
:failed
echo Setup failed. Install Python 3.13 or compatible Python 3 and read the error above.
pause
exit /b 1
