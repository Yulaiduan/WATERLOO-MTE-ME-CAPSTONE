@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto try_python
py -3 preview.py start %*
goto result
:try_python
where python >nul 2>nul
if errorlevel 1 goto missing
python preview.py start %*
:result
if errorlevel 1 (
  echo.
  echo Startup failed. See the message above and .preview\server.log.
  pause
  exit /b 1
)
exit /b 0
:missing
echo Kinefold requires installed Python 3.10 or newer on PATH.
echo Install Python, then double-click this launcher again.
pause
exit /b 1
