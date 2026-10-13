@echo off
rem Open General VSL Solver offline. No server, package install or background service.
rem Input: adjacent v1-kinematics.html. Output: a browser window/tab; units mm/deg.
if not exist "%~dp0v1-kinematics.html" (
  echo Missing v1-kinematics.html. Keep the launcher beside the HTML file.
  pause
  exit /b 1
)
start "" "%~dp0v1-kinematics.html"
