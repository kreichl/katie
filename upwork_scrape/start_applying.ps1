# Set script and project paths
$scriptRoot = $PSScriptRoot
$projectDir = $scriptRoot
$venvPython = Join-Path $scriptRoot "..\.venv\Scripts\python.exe"

Write-Host "Launching Flask server..."
Start-Process -WindowStyle Minimized -FilePath "cmd.exe" `
    -WorkingDirectory $projectDir `
    -ArgumentList "/k `"$venvPython server.py`""

Write-Host "Launching ngrok..."
Start-Process -WindowStyle Minimized -FilePath "cmd.exe" `
    -WorkingDirectory $projectDir `
    -ArgumentList "/k ngrok http 5000"

Write-Host "Waiting for ngrok to initialize..."
Start-Sleep -Seconds 6

Write-Host "Sending ngrok URL to Make.com..."
& $venvPython "$projectDir\push_ngrok_url.py"

Write-Host "All systems running."