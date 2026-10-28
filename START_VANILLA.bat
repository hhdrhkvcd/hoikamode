@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0START_VANILLA.ps1" %*
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo Operation failed. Read the message above. Do not delete your game files.
)
echo.
pause
exit /b %RC%
