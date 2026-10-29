<#
.SYNOPSIS
  Puts a "Studio Hub" shortcut on the Desktop and in the Start Menu.

.DESCRIPTION
  Each shortcut runs Start-Hub.ps1 in a hidden PowerShell window. The Start
  Menu copy carries a global hotkey (default CTRL+ALT+H). The icon is
  hub.ico beside this script, written by make_icon.py from tokens.json; if
  it is missing, PowerShell's own icon is used.

  Carried from Creative-Headquarters' Install-Shortcut.ps1 (both shortcuts
  existed on the laptop). It writes only the two .lnk files and hub.ico.

.PARAMETER Name
  Shortcut name (default 'Studio Hub').
.PARAMETER Hotkey
  Hotkey for the Start Menu copy (default 'CTRL+ALT+H').
.PARAMETER NoHotkey
  Write the Start Menu copy without a hotkey.
#>
param(
  [string]$Name = 'Studio Hub',
  [string]$Hotkey = 'CTRL+ALT+H',
  [switch]$NoHotkey
)

$ErrorActionPreference = 'Stop'
$Start = Join-Path $PSScriptRoot 'Start-Hub.ps1'
$Icon = Join-Path $PSScriptRoot 'hub.ico'
$MakeIcon = Join-Path $PSScriptRoot 'make_icon.py'
if (-not (Test-Path $Start)) { throw "Start-Hub.ps1 is not beside this script." }

if (-not (Test-Path $Icon)) {
  $Python = (Get-Command python.exe -ErrorAction SilentlyContinue), (Get-Command python3.exe -ErrorAction SilentlyContinue) |
    Where-Object { $_ } | Select-Object -First 1
  if ($Python -and (Test-Path $MakeIcon)) { & $Python.Source $MakeIcon $Icon | Out-Null }
}

$Shell = New-Object -ComObject WScript.Shell
$Targets = @(
  @{ Dir = [Environment]::GetFolderPath('Desktop'); Hotkey = '' },
  @{ Dir = [Environment]::GetFolderPath('Programs'); Hotkey = $(if ($NoHotkey) { '' } else { $Hotkey }) }
)
foreach ($t in $Targets) {
  $Path = Join-Path $t.Dir "$Name.lnk"
  $Link = $Shell.CreateShortcut($Path)
  $Link.TargetPath = 'powershell.exe'
  $Link.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Start`""
  $Link.WorkingDirectory = $PSScriptRoot
  $Link.Description = 'Open the ROSW studio hub'
  if (Test-Path $Icon) { $Link.IconLocation = "$Icon,0" }
  if ($t.Hotkey) { $Link.Hotkey = $t.Hotkey }
  $Link.Save()
  Write-Host "wrote $Path$(if ($t.Hotkey) { " (hotkey $($t.Hotkey))" })"
}
