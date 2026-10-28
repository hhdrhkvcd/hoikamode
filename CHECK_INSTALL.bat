@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0CHECK_INSTALL.ps1" %*
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo Check failed. Read the messages above. Do not delete game or save files.
)
echo.
pause
exit /b %RC%
