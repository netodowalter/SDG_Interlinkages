@echo off
rem Download all UNSD SDG observations for one country into output\unsd\UNSD_<code>_2000.csv.
rem Usage: download_unsd.bat [AREA_CODE]   (default 76 = Brazil). Run again to resume if interrupted.
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
set AREA=%~1
if "%AREA%"=="" set AREA=76
".venv\Scripts\python.exe" -X utf8 scripts\download_unsd_country.py %AREA%
if errorlevel 1 goto fail
echo.
echo Done. Attach output\unsd\UNSD_%AREA%_2000.csv in the chat.
pause
exit /b 0
:fail
echo Download failed. Run download_unsd.bat again to resume.
pause
exit /b 1
