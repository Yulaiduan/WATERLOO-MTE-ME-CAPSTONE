@echo off
rem Start local VSL V4 with explicit Excel save/load. Python 3.10+ required.
rem Inputs: adjacent v4 assets; mm/deg/kg/N/Nm. Output: local browser calculator.
rem Local only, port 8767. Close the server window to stop; no automatic startup.
setlocal
set "VSL_PYTHON="
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do if exist "%%~D\python.exe" set "VSL_PYTHON=%%~D\python.exe"
if defined VSL_PYTHON (
  "%VSL_PYTHON%" "%~dp0v4\vsl_server.py" --open
  if errorlevel 1 pause
  exit /b
)
if not exist "%~dp0v4\vsl_server.py" (
  echo Missing v4\vsl_server.py. Keep this launcher in the vsl-solver folder.
  pause
  exit /b 1
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0v4\vsl_server.py" --open
  if errorlevel 1 pause
  exit /b
)
where python >nul 2>nul
if not errorlevel 1 (
  python "%~dp0v4\vsl_server.py" --open
  if errorlevel 1 pause
  exit /b
)
echo Python 3.10 or later is needed for the local Excel bridge.
echo Install Python, then open this launcher again. V4 HTML works without Excel sync.
pause
exit /b 1
