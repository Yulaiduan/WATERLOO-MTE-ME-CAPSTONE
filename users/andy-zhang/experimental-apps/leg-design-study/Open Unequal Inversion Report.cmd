@echo off
setlocal
if not exist "%~dp0unequal-inversion.html" (
  echo Missing unequal-inversion.html beside this launcher.
  pause
  exit /b 1
)
start "" "%~dp0unequal-inversion.html"
exit /b 0
