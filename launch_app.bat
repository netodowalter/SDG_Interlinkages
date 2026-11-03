@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  where py >nul 2>nul
  if errorlevel 1 (
    python -m venv .venv
  ) else (
    py -3 -m venv .venv
  )
  if errorlevel 1 goto fail
)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements-app.txt
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -X utf8 "%~dp0app.py"
if errorlevel 1 goto fail
pause
exit /b 0
:fail
echo Installation or execution failed. See the message above.
pause
exit /b 1
