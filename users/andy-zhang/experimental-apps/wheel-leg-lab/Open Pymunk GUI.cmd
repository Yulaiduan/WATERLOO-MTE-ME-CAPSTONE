@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Python environment missing. Run Setup Pymunk.cmd first.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" "%~dp0debug_gui.py" %*
if errorlevel 1 (
 echo GUI failed. Read the message above, or run Setup Pymunk.cmd to repair dependencies.
 pause
 exit /b 1
)
