@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Stop-Pymunk.ps1" %*
if errorlevel 1 pause
