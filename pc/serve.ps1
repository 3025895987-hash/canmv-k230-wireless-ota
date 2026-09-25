# Serve code/ as static HTTP for CanMV K230 wireless OTA
# Usage:  .\pc\serve.ps1
#         .\pc\serve.ps1 -Port 8000

param(
    [int]$Port = 8000,
    [string]$ProjectRoot = ""
)

$ErrorActionPreference = "Stop"

if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}

$codeDir = Join-Path $ProjectRoot "code"
if (-not (Test-Path (Join-Path $codeDir "main.py"))) {
    Write-Host "ERROR: $codeDir\main.py not found" -ForegroundColor Red
    exit 1
}

$ips = @()
Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -notlike "127.*" -and $_.PrefixOrigin -ne "WellKnown" } |
    ForEach-Object { $ips += $_.IPAddress }

Write-Host "Serving: $codeDir"
Write-Host "Port:    $Port"
Write-Host "PC IPv4: $($ips -join ', ')"
Write-Host ""
foreach ($ip in $ips) {
    Write-Host "  Board URL: http://${ip}:${Port}/main.py"
}
Write-Host ""
Write-Host "Set PC_IP in /sdcard/ota_pull.py to one of the addresses above."
Write-Host "Self-test: http://127.0.0.1:$Port/main.py"
Write-Host "Ctrl+C to stop."
Write-Host ""

Set-Location $codeDir
$py = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $py = "py" }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $py = "python" }
else {
    Write-Host "ERROR: python/py not found" -ForegroundColor Red
    exit 1
}

& $py -m http.server $Port
