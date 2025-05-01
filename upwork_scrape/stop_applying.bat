@echo off
setlocal

echo Stopping ngrok and Flask...

REM --- Kill python server.py ---
powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*server.py*' } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force } catch {} }"

REM --- Kill ngrok ---
powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*ngrok*' } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force } catch {} }"

REM --- Wait briefly to ensure processes are killed ---
timeout /t 2 >nul

REM --- Send shutdown webhook ---
echo Notifying Make.com...
python send_webhook.py
