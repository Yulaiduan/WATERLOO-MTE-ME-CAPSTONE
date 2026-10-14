@echo off
setlocal
if not exist "%~dp0curved-paths.html" (
  echo Missing report: "%~dp0curved-paths.html"
  echo Restore this app folder from Git and try again.
  pause
  exit /b 1
)
start "" "%~dp0curved-paths.html"
if errorlevel 1 (
  echo Could not open the report. Open curved-paths.html manually in a browser.
  pause
  exit /b 1
)
exit /b 0
