$ErrorActionPreference = 'Stop'
$taskStatePath = Join-Path $PSScriptRoot '.preview\capstone-server.json'
function Archive-CapstoneState {
    $taskHistory = Join-Path $PSScriptRoot '.preview\history'
    New-Item -ItemType Directory -Force -Path $taskHistory | Out-Null
    Move-Item -LiteralPath $taskStatePath -Destination (Join-Path $taskHistory ('capstone-' + [guid]::NewGuid().ToString() + '.json'))
}
try {
    if (!(Test-Path -LiteralPath $taskStatePath)) { Write-Host 'No tracked Capstone server. Nothing was stopped.'; exit 0 }
    $state = Get-Content -LiteralPath $taskStatePath -Raw | ConvertFrom-Json
    $server = Get-CimInstance Win32_Process -Filter "ProcessId=$($state.pid)"
    if (!$server) { Archive-CapstoneState; Write-Host 'Tracked Capstone server already stopped.'; exit 0 }
    $expectedNode = $state.executable
    $expectedVite = Join-Path $PSScriptRoot 'node_modules\vite\bin\vite.js'
    if (!$expectedNode -or [System.IO.Path]::GetFileName($expectedNode) -ne 'node.exe' -or
        $server.CreationDate.ToUniversalTime().ToString('o') -ne $state.creationTimeUtc -or
        $server.ExecutablePath -ne $expectedNode -or $state.projectRoot -ne $PSScriptRoot -or
        $state.port -ne 4175 -or $state.vitePath -ne $expectedVite -or
        !$server.CommandLine.Contains($expectedVite) -or
        $server.CommandLine -notmatch '--host\s+127\.0\.0\.1' -or
        $server.CommandLine -notmatch '--port\s+4175(?:\s|$)' -or
        $server.CommandLine -notmatch '--strictPort') { throw 'Tracked PID no longer matches this Capstone server. Nothing was stopped.' }
    Stop-Process -Id $server.ProcessId
    Archive-CapstoneState
    Write-Host 'Terrain Atlas preview stopped. Double-click Start Terrain Atlas.cmd to restart.'
} catch { Write-Host "STOP FAILED: $($_.Exception.Message)" -ForegroundColor Red; exit 1 }
