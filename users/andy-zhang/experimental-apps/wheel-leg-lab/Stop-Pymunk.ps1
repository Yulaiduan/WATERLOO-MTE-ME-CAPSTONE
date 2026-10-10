param([ValidateSet(4186,4175)][int]$Port=4186)
$ErrorActionPreference='Stop'
$taskStateFile=Join-Path $PSScriptRoot ".preview\server-$Port.json"
try {
    if(!(Test-Path -LiteralPath $taskStateFile)) { Write-Host 'No tracked server; nothing was stopped.'; exit 0 }
    $state=Get-Content -LiteralPath $taskStateFile -Raw | ConvertFrom-Json
    $server=Get-CimInstance Win32_Process -Filter "ProcessId=$($state.pid)"
    if(!$server) { Remove-Item -LiteralPath $taskStateFile; Write-Host 'Server already stopped.'; exit 0 }
    $taskServer=Join-Path $PSScriptRoot 'server.py'
    $taskPython=Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    if($state.root -ne $PSScriptRoot -or $server.CreationDate.ToUniversalTime().ToString('o') -ne $state.created -or !$server.CommandLine.Contains($taskServer) -or !$server.CommandLine.Contains($taskPython) -or $state.port -ne $Port -or $server.CommandLine -notmatch "--port\s+$Port(?:\s|$)") {
        throw 'Tracked process no longer matches this app; nothing was stopped.'
    }
    Stop-Process -Id $server.ProcessId
    Remove-Item -LiteralPath $taskStateFile
    Write-Host 'Pymunk linkage stopped. Double-click Start Pymunk Linkage.cmd to restart.'
} catch { Write-Host "STOP FAILED: $($_.Exception.Message)" -ForegroundColor Red; exit 1 }
