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
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -X utf8 -m ods %*
if errorlevel 1 goto fail
if "%~1"=="" pause
exit /b 0
:fail
echo Falha na instalacao ou execucao. Veja a mensagem acima.
if "%~1"=="" pause
exit /b 1
