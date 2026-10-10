@echo off
call "%~dp0..\wheel-leg-lab\Start Motion Lab.cmd" -NoBrowser
if errorlevel 1 exit /b 1
if /i not "%~1"=="-NoBrowser" start "" "http://127.0.0.1:4186/?tab=studies&study=ratio"
