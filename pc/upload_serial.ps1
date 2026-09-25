# Upload a local file to CanMV K230 over COM3 using base64 + ubinascii
param(
    [Parameter(Mandatory=$true)][string]$LocalPath,
    [Parameter(Mandatory=$true)][string]$RemotePath,
    [string]$ComPort = "COM3",
    [int]$Baud = 115200,
    [int]$Chunk = 180
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $LocalPath)) { throw "Local file not found: $LocalPath" }
$bytes = [System.IO.File]::ReadAllBytes($LocalPath)
$b64 = [Convert]::ToBase64String($bytes)
Write-Host "Local $LocalPath size=$($bytes.Length) b64len=$($b64.Length) -> $RemotePath"

$port = New-Object System.IO.Ports.SerialPort $ComPort,$Baud,"None",8,"One"
$port.ReadTimeout = 15000
$port.WriteTimeout = 15000
$port.DtrEnable = $true
$port.RtsEnable = $true
$port.Open()
Start-Sleep -Milliseconds 250

function Send-Line([string]$line, [int]$waitMs = 80) {
    $port.DiscardInBuffer()
    $port.Write($line + "`r`n")
    if ($waitMs -gt 0) { Start-Sleep -Milliseconds $waitMs }
}

function Wait-Prompt([int]$timeoutMs = 3000) {
    $buf = ""
    $start = Get-Date
    while (((Get-Date) - $start).TotalMilliseconds -lt $timeoutMs) {
        try {
            $chunk = $port.ReadExisting()
            if ($chunk) { $buf += $chunk }
        } catch {}
        if ($buf -match ">>>") { return $buf }
        Start-Sleep -Milliseconds 50
    }
    return $buf
}

# interrupt
$port.DiscardInBuffer()
$port.Write([string][char]3); Start-Sleep -Milliseconds 150
$port.Write([string][char]3); Start-Sleep -Milliseconds 250
$port.DiscardInBuffer()

Write-Host "Init remote file..."
Send-Line "import ubinascii" 200
Send-Line "f=open('$RemotePath','wb')" 200
$out = Wait-Prompt
Write-Host "open: $($out -replace \"`r|`n\", ' ')"

$total = $b64.Length
$offset = 0
$i = 0
while ($offset -lt $total) {
    $len = [Math]::Min($Chunk, $total - $offset)
    $piece = $b64.Substring($offset, $len)
    Send-Line "f.write(ubinascii.a2b_base64('$piece'))" 40
    $offset += $len
    $i++
    if ($i % 20 -eq 0) {
        $ack = Wait-Prompt 800
        Write-Host "chunk $i offset=$offset/$total ack=$($ack.Length)"
    }
}

Write-Host "Close remote file..."
Send-Line "f.close()" 300
Send-Line "import os;print('SIZE', os.stat('$RemotePath')[6])" 800
$out = Wait-Prompt 3000
Write-Host "RESULT:"
Write-Host $out
$port.Close()
Write-Host "Upload done."
