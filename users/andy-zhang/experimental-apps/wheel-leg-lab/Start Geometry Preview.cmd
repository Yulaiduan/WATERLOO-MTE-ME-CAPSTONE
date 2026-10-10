@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Pymunk.ps1" -Port 4175 -NoBrowser
if errorlevel 1 (
 echo Port 4175 may belong to another preview. Nothing was stopped. Use its own stop launcher first.
 pause
 exit /b 1
)
if /i not "%~1"=="-NoBrowser" start "" "http://127.0.0.1:4175/force-plots/"
