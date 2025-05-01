# Set paths
$scriptRoot = $PSScriptRoot
$venvPython = Join-Path $scriptRoot "..\.venv\Scripts\python.exe"
$webhookScript = Join-Path $scriptRoot "send_webhook.py"

Write-Host "Stopping ngrok and Flask..."

Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*server.py*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*ngrok*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

Start-Sleep -Seconds 2

Write-Host "Notifying Make.com..."
& $venvPython $webhookScript