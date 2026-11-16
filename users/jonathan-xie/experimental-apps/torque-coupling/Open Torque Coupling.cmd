@echo off
rem Open the interactive app in the default browser; server stays in background.
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -B launcher.py
) else (
  python -B launcher.py
)
if errorlevel 1 pause
