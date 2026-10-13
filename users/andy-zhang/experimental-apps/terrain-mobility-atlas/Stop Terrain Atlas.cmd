@echo off
rem Stop only this app's verified standalone Node/Vite server and archive its state.
rem No inputs; outputs: status text. Refuses mismatched PID, folder, time or port.
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Stop-Capstone.ps1" %*
if errorlevel 1 (
 echo Terrain Atlas could not be stopped. Read the message above.
 pause
 exit /b 1
)
