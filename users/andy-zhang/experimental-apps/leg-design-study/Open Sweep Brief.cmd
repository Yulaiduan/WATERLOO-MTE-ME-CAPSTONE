@echo off
setlocal
if not exist "%~dp0design-sweep-brief.html" (
  echo Missing design-sweep-brief.html beside this launcher.
  pause
  exit /b 1
)
start "" "%~dp0design-sweep-brief.html"
exit /b 0
