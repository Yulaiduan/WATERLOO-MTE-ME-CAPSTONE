param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
try {
    & powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'Start-Capstone.ps1') -NoBrowser
    if ($LASTEXITCODE -ne 0) { throw 'Capstone server startup failed.' }
    $taskForceUrl = 'http://127.0.0.1:4175/force-plots/'
    $response = Invoke-WebRequest -Uri $taskForceUrl -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -ne 200 -or !$response.Content.Contains('id="wheel-leg-force"')) {
        throw 'Force plots are missing from the saved build. Run npm run build in this project.'
    }
    Write-Host "Force plots ready: $taskForceUrl"
    Write-Host "Stop using Stop Capstone.cmd in $PSScriptRoot."
    if (!$NoBrowser) { Start-Process $taskForceUrl }
} catch { Write-Host "START FAILED: $($_.Exception.Message)" -ForegroundColor Red; exit 1 }
