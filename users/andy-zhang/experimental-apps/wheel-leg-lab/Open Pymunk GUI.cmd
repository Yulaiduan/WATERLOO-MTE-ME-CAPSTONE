@echo off
call "%~dp0Start Motion Lab.cmd" -NoBrowser
if errorlevel 1 exit /b 1
start "" "http://127.0.0.1:4186/?gui=1"
