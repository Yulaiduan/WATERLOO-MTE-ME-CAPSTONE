param([switch]$NoBrowser,[ValidateSet(4186,4175)][int]$Port=4186)
$ErrorActionPreference='Stop'
$taskRoot=$PSScriptRoot
$taskPython=Join-Path $taskRoot '.venv\Scripts\python.exe'
$taskServer=Join-Path $taskRoot 'server.py'
$taskStateDir=Join-Path $taskRoot '.preview'
$taskStateFile=Join-Path $taskStateDir "server-$Port.json"
$taskUrl="http://127.0.0.1:$Port/"
function Test-PymunkProcess($candidate) {
    return $candidate -and $candidate.CommandLine.Contains($taskServer) -and
        $candidate.CommandLine.Contains($taskPython) -and $candidate.Name -eq 'python.exe' -and $candidate.CommandLine -match "--port\s+$Port(?:\s|$)"
}
function Test-PymunkHttp {
    try {
        $health=Invoke-RestMethod -Uri ($taskUrl+'api/health') -TimeoutSec 2
        $page=Invoke-WebRequest -Uri $taskUrl -UseBasicParsing -TimeoutSec 2
        return $health.app -eq 'capstone-wheel-leg-lab' -and $health.root -eq $taskRoot -and
            $page.StatusCode -eq 200 -and $page.Content.Contains('pymunk-suspension-bench')
    } catch { return $false }
}
try {
    Set-Location -LiteralPath $taskRoot
    foreach($required in @($taskPython,$taskServer,(Join-Path $taskRoot 'web\index.html'),(Join-Path $taskRoot 'web\animations\index.html'),(Join-Path $taskRoot 'web\linkage\index.html'))) {
        if(!(Test-Path -LiteralPath $required)) { throw "Missing prerequisite: $required. Run Setup Pymunk.cmd in this folder, including npm run build." }
    }
    New-Item -ItemType Directory -Force -Path $taskStateDir | Out-Null
    $listeners=@(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
    if($listeners.Count) {
        $owners=@($listeners.OwningProcess | Select-Object -Unique)
        if($owners.Count -ne 1) { throw 'Port $Port has multiple owners; nothing was stopped.' }
        $server=Get-CimInstance Win32_Process -Filter "ProcessId=$($owners[0])"
        if(!(Test-PymunkProcess $server) -or !(Test-PymunkHttp)) { throw 'Port $Port belongs to another or unready app; nothing was stopped.' }
        Write-Host 'Pymunk linkage is already running; reusing verified server.'
    } else {
        $started=Start-Process -FilePath $taskPython -ArgumentList @('-u',('"'+$taskServer+'"'),'--port',$Port) -WorkingDirectory $taskRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskStateDir 'server.stdout.log') -RedirectStandardError (Join-Path $taskStateDir 'server.stderr.log') -PassThru
        $deadline=[DateTime]::UtcNow.AddSeconds(25)
        $ready=$false
        while([DateTime]::UtcNow -lt $deadline) {
            if(Test-PymunkHttp) { $ready=$true; break }
            if($started.HasExited) { throw 'Server exited. Inspect .preview/server.stderr.log.' }
            Start-Sleep -Milliseconds 250
        }
        if(!$ready) { throw 'HTTP readiness timed out; inspect .preview logs.' }
        $listener=Get-NetTCPConnection -LocalPort $Port -State Listen | Select-Object -First 1
        $server=Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
        if(!(Test-PymunkProcess $server)) { throw 'Started server could not be identified.' }
    }
    @{pid=$server.ProcessId;created=$server.CreationDate.ToUniversalTime().ToString('o');root=$taskRoot;server=$taskServer;port=$Port} | ConvertTo-Json | Set-Content -LiteralPath $taskStateFile -Encoding UTF8
    Write-Host "Ready: $taskUrl"
    Write-Host "Stop with Stop Pymunk Linkage.cmd in $taskRoot. Logs: .preview"
    if(!$NoBrowser) { Start-Process $taskUrl }
} catch { Write-Host "START FAILED: $($_.Exception.Message)" -ForegroundColor Red; exit 1 }
