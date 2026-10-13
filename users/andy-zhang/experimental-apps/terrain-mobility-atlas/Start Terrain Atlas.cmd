@echo off
rem Start the standalone atlas from this project using installed Node.js on PATH.
rem Inputs: optional -NoBrowser; output: verified localhost:4175 pages and logs.
rem This experimental preview is independent of the Motion Lab compatibility aliases.
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Capstone.ps1" %*
if errorlevel 1 (
 echo Terrain Atlas failed to start. Read the message above.
 pause
 exit /b 1
)
