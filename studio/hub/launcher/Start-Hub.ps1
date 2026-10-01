<#
.SYNOPSIS
  One-press launcher for the ROSW studio hub on Windows.

.DESCRIPTION
  Starts, or reuses, the hub server (studio/hub/serve.py, bound to 127.0.0.1)
  and opens it in the default browser. The server serves only studio/hub/ and
  the studio's JSON routes; it never serves the repo root.

  Carried from Creative-Headquarters' Start-Hub.ps1, which was in daily use
  through its shortcuts. Changes: it runs serve.py instead of a bare
  http.server on the repo root; there is one port range; a running hub is
  recognised by the /api/mark route.

.PARAMETER Port
  First port to try (default 8765). The range is Port..Port+PortSearch-1.
.PARAMETER PortSearch
  How many ports to probe (default 10).
.PARAMETER Stop
  Stop every hub server found in the range instead of starting one.
.PARAMETER NoBrowser
  Start or reuse the server without opening a browser.

.EXAMPLE
  .\Start-Hub.ps1
  .\Start-Hub.ps1 -Port 8800 -NoBrowser
  .\Start-Hub.ps1 -Stop
#>
param(
  [ValidateRange(1024, 65535)][int]$Port = 8765,
  [ValidateRange(1, 50)][int]$PortSearch = 10,
  [switch]$Stop,
  [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'
$Mark = 'ROSW studio hub'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$Serve = Join-Path $Root 'studio\hub\serve.py'
if (-not (Test-Path $Serve)) {
  throw "Could not find studio\hub\serve.py under '$Root'. Keep Start-Hub.ps1 in studio\hub\launcher\."
}

function Test-PortInUse([int]$p) {
  $client = New-Object System.Net.Sockets.TcpClient
  try { $client.Connect('127.0.0.1', $p); return $true } catch { return $false } finally { $client.Dispose() }
}

function Test-HubServer([int]$p) {
  if (-not (Test-PortInUse $p)) { return $false }
  try {
    $reply = Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 -Uri "http://127.0.0.1:$p/api/mark"
    return ($reply.StatusCode -eq 200) -and ($reply.Content -match [regex]::Escape($Mark))
  } catch { return $false }
}

$Range = $Port..($Port + $PortSearch - 1)

if ($Stop) {
  $stopped = 0
  foreach ($p in $Range) {
    if (Test-HubServer $p) {
      Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object { Stop-Process -Id $_ -Force; $stopped++ }
    }
  }
  if ($stopped) { Write-Host "Stopped $stopped hub server process(es)." } else { Write-Host 'No hub server was running.' }
  return
}

$Chosen = $null
foreach ($p in $Range) { if (Test-HubServer $p) { $Chosen = $p; break } }

if (-not $Chosen) {
  $Free = $null
  foreach ($p in $Range) { if (-not (Test-PortInUse $p)) { $Free = $p; break } }
  if (-not $Free) { throw "Ports $Port-$($Range[-1]) are all in use. Pass -Port with a free one." }

  $Python = (Get-Command python.exe -ErrorAction SilentlyContinue), (Get-Command python3.exe -ErrorAction SilentlyContinue) |
    Where-Object { $_ } | Select-Object -First 1
  if (-not $Python) {
    throw "Python was not found on PATH. Install Python 3, or run: python studio\hub\serve.py --port $Free"
  }
  # python.exe, not pythonw.exe: serve.py logs to stderr, which pythonw has none of.
  Start-Process -FilePath $Python.Source -ArgumentList @($Serve, '--port', $Free, '--quiet') `
    -WorkingDirectory $Root -WindowStyle Hidden
  $deadline = (Get-Date).AddSeconds(15)
  while ((Get-Date) -lt $deadline) {
    if (Test-HubServer $Free) { $Chosen = $Free; break }
    Start-Sleep -Milliseconds 250
  }
  if (-not $Chosen) { throw "Server on port $Free did not come up within 15s." }
}

$Url = "http://127.0.0.1:$Chosen/"
Write-Host "$Mark is live at $Url"
if (-not $NoBrowser) { Start-Process $Url }
