@echo off
rem Open the standalone General VSL quasi-static solver in the default browser.
rem Input: adjacent v2-quasi-static.html, mm/deg/kg/N/Nm. No server/dependencies.
if not exist "%~dp0v2-quasi-static.html" (
  echo Missing v2-quasi-static.html. Keep this launcher beside the HTML file.
  pause
  exit /b 1
)
start "" "%~dp0v2-quasi-static.html"
