@echo off
rem Open the static alpha-zero path report beside this launcher; no runtime or server needed.
if not exist "%~dp0inversion-paths.html" (
  echo Missing inversion-paths.html. Keep the report folder together.
  pause
  exit /b 1
)
start "" "%~dp0inversion-paths.html"
