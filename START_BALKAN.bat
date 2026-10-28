@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0START_BALKAN.ps1"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo Script failed. Read the message above; previous settings were backed up.
)
echo.
pause
exit /b %RC%
