$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)

chcp 65001 > $null

$projectRoot = "D:\smart_compras\backend"
$pythonExe = "python"
$scriptPath = Join-Path $projectRoot "scripts\importar_atacadao.py"
$logDir = Join-Path $projectRoot "logs"

if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Force $logDir | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = Join-Path $logDir "importar_atacadao_$timestamp.log"

Set-Location $projectRoot

"===== INICIO $timestamp =====" | Out-File -FilePath $logFile -Encoding utf8
& $pythonExe $scriptPath 2>&1 | Out-File -FilePath $logFile -Encoding utf8 -Append
"===== FIM $(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss') =====" | Out-File -FilePath $logFile -Encoding utf8 -Append

Get-Content $logFile
