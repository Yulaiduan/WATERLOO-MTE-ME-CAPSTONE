@echo off
rem Open the static offline design report beside this launcher. No server or runtime needed.
if not exist "%~dp0index.html" (
  echo Missing index.html. Keep the report folder together.
  pause
  exit /b 1
)
start "" "%~dp0index.html"
