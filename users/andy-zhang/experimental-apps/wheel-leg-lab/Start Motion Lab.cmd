@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Pymunk.ps1" %*
if errorlevel 1 (
 echo Motion Lab failed to start. Read the message above.
 pause
 exit /b 1
)
