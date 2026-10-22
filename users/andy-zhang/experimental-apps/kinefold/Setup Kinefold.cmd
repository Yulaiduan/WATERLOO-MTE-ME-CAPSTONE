@echo off
rem Purpose: install Kinefold's own dynamics runtime. Run by double-clicking.
rem Inputs: installed Python 3.12+, adjacent pinned requirements; units N/A.
rem Output: project-local .venv. Experimental models; no hardware validation.
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 goto missing
python -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)"
if errorlevel 1 goto missing
if not exist ".venv\Scripts\python.exe" python -m venv ".venv"
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -c "import pymunk, scipy; print('Kinefold dynamics ready. Pymunk',pymunk.version,'SciPy',scipy.__version__)"
if errorlevel 1 goto failed
echo Setup complete. Start Kinefold.cmd opens the existing app at port 4191.
pause
exit /b 0
:missing
echo Install Python 3.12 or newer with pip, then rerun this launcher.
:failed
echo Setup failed. Read the error above, resolve it, and rerun Setup Kinefold.cmd.
pause
exit /b 1
