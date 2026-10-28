@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0RESTORE_PREVIOUS_MODS.ps1"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo Restore failed. Read the message above.
)
echo.
pause
exit /b %RC%
