@echo off
setlocal
if not exist "%~dp0rms-link-comparison.html" (
  echo Missing rms-link-comparison.html beside this launcher.
  pause
  exit /b 1
)
start "" "%~dp0rms-link-comparison.html"
exit /b 0
