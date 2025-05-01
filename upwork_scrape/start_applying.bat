@echo off
setlocal

REM --- Activate virtual environment ---
echo Activating virtual environment...
call ..\.venv\Scripts\activate.bat

REM --- Start Flask server in a new terminal ---
echo Launching Flask server...
start "FLASK_SERVER" cmd /k python server.py

REM --- Start ngrok tunnel in a new terminal ---
echo Launching ngrok...
start "NGROK_TUNNEL" cmd /k ngrok http 5000

REM --- Wait a few seconds for ngrok to initialize ---
timeout /t 6 >nul

REM --- Send ngrok URL to Make ---
echo Determining ngrok URL
python push_ngrok_url.py

echo All systems running.
pause
endlocal