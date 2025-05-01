@echo off
setlocal

echo Stopping ngrok and Flask...

REM --- Kill ngrok and Flask by process name ---
taskkill /f /im ngrok.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1

echo ngrok and Flask stopped.

REM ---  Send shutdown webhook to Make.com ---
echo Notifying Make.com...
python send_webhook.py

