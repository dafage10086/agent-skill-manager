@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul || (echo Python was not found in PATH. & exit /b 1)
set "SCRIPT=skills\auto-skill-installer\scripts\auto_install.py"
if /I "%~1"=="--self-test" (
  python "%SCRIPT%" --help >nul
  if errorlevel 1 exit /b 1
  exit /b 0
)
echo [Auto Skill Installer]
echo Example: github pull request review comments
echo.
set /p "NEED=Enter skill need, or press Enter for the example: "
if "%NEED%"=="" set "NEED=github pull request review comments"
echo.
echo 1. Search only
echo 2. Ensure/install top match (may write to CODEX_HOME skills)
choice /C 12 /M "Choose mode"
set "SEL=%ERRORLEVEL%"
if "%SEL%"=="2" (
  python "%SCRIPT%" ensure --need "%NEED%" --force
) else (
  python "%SCRIPT%" search --need "%NEED%"
)
set "CODE=%ERRORLEVEL%"
echo.
echo Finished with exit code %CODE%.
echo Press any key to close this window.
pause >nul
exit /b %CODE%