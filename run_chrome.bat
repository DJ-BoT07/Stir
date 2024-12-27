@echo off
echo Starting Chrome with remote debugging...

:: Kill any existing Chrome instances
taskkill /F /IM "chrome.exe" /T >nul 2>&1

:: Start Chrome with remote debugging using default profile
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

:: Wait a bit longer for Chrome to start
timeout /t 5

:: Try to get the debugging URL
:retry
curl -s http://localhost:9222/json/version
if %ERRORLEVEL% NEQ 0 (
    echo Waiting for Chrome to start...
    timeout /t 2
    goto retry
)

echo.
echo If you see JSON output above, copy the "webSocketDebuggerUrl" value
echo Example: node src/index.js "ws://127.0.0.1:9222/devtools/browser/..."
echo.
echo Press any key to close this window...
pause >nul 