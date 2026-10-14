@echo off
setlocal
if not exist "%~dp0force-travel.html" (
  echo Force and travel report is missing from this folder.
  pause
  exit /b 1
)
start "" "%~dp0force-travel.html"
exit /b 0
