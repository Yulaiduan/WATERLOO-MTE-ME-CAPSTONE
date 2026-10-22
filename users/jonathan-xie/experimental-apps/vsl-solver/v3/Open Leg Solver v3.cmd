@echo off
rem Open standalone VSL V3. Input: adjacent HTML, mm/deg/kg/N/Nm; no server.
rem Output: default browser window. No installation or automatic startup.
if not exist "%~dp0v3-spring.html" (
  echo Missing v3-spring.html. Keep this launcher beside the HTML file.
  pause
  exit /b 1
)
start "" "%~dp0v3-spring.html"
