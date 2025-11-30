# start_and_test.ps1
# Start the Flask app in mock mode, wait for port 5000, run the external smoke test, then stop the server.

param(
    [int]$Port = 5000,
    [int]$TimeoutSec = 20
)

Write-Host "Starting Flask app in mock mode..."
$env:RAZORPAY_MOCK = '1'
$env:RAZORPAY_KEY_ID = 'rzp_test_placeholder'
$env:RAZORPAY_KEY_SECRET = 'placeholder_secret'

$python = Join-Path -Path $PSScriptRoot -ChildPath ".\.venv\Scripts\python.exe"
$startInfo = @{ FilePath = $python; ArgumentList = 'app.py'; PassThru = $true }
$proc = Start-Process @startInfo
Write-Host "Started process ID: $($proc.Id)"

# wait until port is listening
$start = Get-Date
while ((Get-Date) -lt $start.AddSeconds($TimeoutSec)) {
    Start-Sleep -Milliseconds 300
    $list = netstat -ano | Select-String ":$Port"
    if ($list) { break }
}

if (-not $list) {
    Write-Host "Server did not start listening on port $Port within $TimeoutSec seconds."
    Write-Host "Killing process $($proc.Id)"
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Server listening on port $Port, running smoke test..."
try {
    .\.venv\Scripts\python.exe test_payment_smoke.py
} catch {
    Write-Host "Smoke test failed: $_"
}

Write-Host "Stopping server (PID $($proc.Id))"
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
Write-Host "Done."