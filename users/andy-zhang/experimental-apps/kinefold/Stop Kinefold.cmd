@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto try_python
py -3 preview.py stop
goto result
:try_python
where python >nul 2>nul
if errorlevel 1 goto missing
python preview.py stop
:result
if errorlevel 1 (
  echo Stop failed. The unrelated process, if any, was left untouched.
  pause
  exit /b 1
)
exit /b 0
:missing
echo Python 3.10 or newer is required to stop this preview.
pause
exit /b 1
