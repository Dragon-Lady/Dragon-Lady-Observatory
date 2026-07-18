@echo off
setlocal EnableExtensions

REM Dragon Lady Observatory — double-click launcher (Windows)
REM Starts the Astro viewer at http://127.0.0.1:4331/observatory

set "ROOT=%~dp0.."
set "VIEWER=%ROOT%\viewer"
set "PORT=4331"
set "HOST=127.0.0.1"

if not exist "%VIEWER%\package.json" (
  echo Could not find viewer\package.json under:
  echo   %ROOT%
  pause
  exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
  echo npm / Node.js not found. Install Node 20+ then try again.
  pause
  exit /b 1
)

cd /d "%VIEWER%" || exit /b 1

if not exist "node_modules\astro" (
  echo First run — npm install …
  call npm install
  if errorlevel 1 (
    echo npm install failed.
    pause
    exit /b 1
  )
)

echo === Dragon Lady Observatory ===
echo Wait for:  Local  http://%HOST%:%PORT%/
echo Then open: http://127.0.0.1:%PORT%/observatory
echo Leave this window open while you explore.
echo.

REM Open the browser shortly after start (dev server may still be booting)
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:%PORT%/observatory"

call npx astro dev --host %HOST% --port %PORT%
exit /b %ERRORLEVEL%
