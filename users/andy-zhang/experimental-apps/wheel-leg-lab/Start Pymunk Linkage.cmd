@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Pymunk.ps1" %*
if errorlevel 1 (
 echo.
 echo Startup failed. Read the message above and .preview logs in this folder.
 pause
 exit /b 1
)
exit /b 0
