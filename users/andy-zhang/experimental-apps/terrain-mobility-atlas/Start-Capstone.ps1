param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$taskProjectRoot = $PSScriptRoot
$taskNodePath = 'C:\Program Files\nodejs\node.exe'
$taskVitePath = Join-Path $taskProjectRoot 'node_modules\vite\bin\vite.js'
$taskStateDir = Join-Path $taskProjectRoot '.preview'
$taskStatePath = Join-Path $taskStateDir 'capstone-server.json'
$taskUrls = @('http://127.0.0.1:4175/', 'http://127.0.0.1:4175/workbench/', 'http://127.0.0.1:4175/linkage/')

function Test-CapstoneProcess($candidate) {
    return $candidate -and $candidate.ExecutablePath -eq $taskNodePath -and
        $candidate.CommandLine.Contains($taskVitePath) -and
        $candidate.CommandLine -match '--host\s+127\.0\.0\.1' -and
        $candidate.CommandLine -match '--port\s+4175(?:\s|$)' -and
        $candidate.CommandLine -match '--strictPort'
}
function Test-CapstoneHttp {
    try {
        for ($i = 0; $i -lt $taskUrls.Count; $i++) {
            $response = Invoke-WebRequest -Uri $taskUrls[$i] -UseBasicParsing -TimeoutSec 2
            $marker = @('/assets/atlas-', '/assets/workbench-', '/assets/linkage-')[$i]
            if ($response.StatusCode -ne 200 -or !$response.Content.Contains($marker)) { return $false }
        }
        return $true
    } catch { return $false }
}
try {
    Set-Location -LiteralPath $taskProjectRoot
    foreach ($required in @($taskNodePath, $taskVitePath, (Join-Path $taskProjectRoot 'dist\index.html'), (Join-Path $taskProjectRoot 'dist\workbench\index.html'), (Join-Path $taskProjectRoot 'dist\linkage\index.html'))) {
        if (!(Test-Path -LiteralPath $required)) { throw "Missing prerequisite: $required. Install Node.js if needed, then run npm ci and npm run build in $taskProjectRoot." }
    }
    New-Item -ItemType Directory -Path $taskStateDir -Force | Out-Null
    $listeners = @(Get-NetTCPConnection -LocalPort 4175 -State Listen -ErrorAction SilentlyContinue)
    if ($listeners.Count) {
        $owners = @($listeners.OwningProcess | Select-Object -Unique)
        if ($owners.Count -ne 1) { throw 'Port 4175 has multiple owners. Close the conflicting application before retrying.' }
        $server = Get-CimInstance Win32_Process -Filter "ProcessId=$($owners[0])"
        if (!(Test-CapstoneProcess $server) -or !(Test-CapstoneHttp)) { throw 'Port 4175 is occupied by another process or an unready app. Nothing was stopped. Close the conflict and retry.' }
        Write-Host 'Capstone is already running; reusing the verified server.'
    } else {
        foreach ($taskLogName in @('server.stdout.log','server.stderr.log')) {
            $taskPreviousLog=Join-Path $taskStateDir $taskLogName
            if (Test-Path -LiteralPath $taskPreviousLog) {
                $taskLogHistory=Join-Path $taskStateDir 'history'
                New-Item -ItemType Directory -Force -Path $taskLogHistory | Out-Null
                Move-Item -LiteralPath $taskPreviousLog -Destination (Join-Path $taskLogHistory ([guid]::NewGuid().ToString()+'-'+$taskLogName))
            }
        }
        $arguments = @(('"' + $taskVitePath + '"'), 'preview', '--host', '127.0.0.1', '--port', '4175', '--strictPort')
        $started = Start-Process -FilePath $taskNodePath -ArgumentList $arguments -WorkingDirectory $taskProjectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskStateDir 'server.stdout.log') -RedirectStandardError (Join-Path $taskStateDir 'server.stderr.log') -PassThru
        $server = Get-CimInstance Win32_Process -Filter "ProcessId=$($started.Id)"
        if (!(Test-CapstoneProcess $server)) { throw 'Started process could not be identified. Inspect .preview logs.' }
        @{ pid = $server.ProcessId; creationTimeUtc = $server.CreationDate.ToUniversalTime().ToString('o'); executable = $taskNodePath; vitePath = $taskVitePath; projectRoot = $taskProjectRoot; port = 4175 } | ConvertTo-Json | Set-Content -LiteralPath $taskStatePath -Encoding UTF8
        $ready = $false
        $deadline = [DateTime]::UtcNow.AddSeconds(25)
        while ([DateTime]::UtcNow -lt $deadline) {
            if (Test-CapstoneHttp) { $ready = $true; break }
            if ($started.HasExited) { throw 'Capstone server exited during startup. Inspect .preview/server.stderr.log.' }
            Start-Sleep -Milliseconds 250
        }
        if (!$ready) { throw 'Capstone HTTP readiness timed out. Inspect .preview logs and use Stop Capstone.cmd before retrying.' }
    }
    @{ pid = $server.ProcessId; creationTimeUtc = $server.CreationDate.ToUniversalTime().ToString('o'); executable = $taskNodePath; vitePath = $taskVitePath; projectRoot = $taskProjectRoot; port = 4175 } | ConvertTo-Json | Set-Content -LiteralPath $taskStatePath -Encoding UTF8
    Write-Host 'Ready: http://127.0.0.1:4175/ ; http://127.0.0.1:4175/workbench/ ; http://127.0.0.1:4175/linkage/'
    Write-Host "Stop with Stop Capstone.cmd in $taskProjectRoot. Logs: .preview"
    if (!$NoBrowser) { foreach ($url in $taskUrls) { Start-Process $url } }
} catch { Write-Host "START FAILED: $($_.Exception.Message)" -ForegroundColor Red; exit 1 }
