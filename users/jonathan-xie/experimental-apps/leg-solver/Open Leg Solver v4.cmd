@echo off
rem Open standalone VSL V4. Input: adjacent HTML, mm/deg/kg/N/Nm; no server.
rem Output: default browser window. No installation or automatic startup.
if not exist "%~dp0v4-pulley.html" (
  echo Missing v4-pulley.html. Keep this launcher beside the HTML file.
  pause
  exit /b 1
)
start "" "%~dp0v4-pulley.html"
