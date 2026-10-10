@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Force-Plots.ps1" %*
if errorlevel 1 (
  echo.
  echo Force plots did not start. Read the message above and .preview logs.
  pause
  exit /b 1
)
exit /b 0
