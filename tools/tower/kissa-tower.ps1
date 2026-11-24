#Requires -RunAsAdministrator
<#
.SYNOPSIS
  Richtet den Windows-Tower als Backup-Ziel für kissa ein.

.DESCRIPTION
  - restic rest-server als Dienst beim Systemstart (läuft ohne Anmeldung), Modus "append-only":
    der Laptop kann Sicherungen hinzufügen, aber nichts löschen (Schutz gegen Ransomware).
  - Firewall: Port 8000 nur aus dem Heimnetz.
  - Wake-on-LAN an der Netzwerkkarte einschalten, Windows-Schnellstart aus.
  - Auto-Shutdown: Wurde der Tower geweckt und meldet sich niemand an, fährt er
    15 Minuten nach dem letzten Backup-Zugriff wieder herunter.
  Erneut ausführen ist unbedenklich (Passwort bleibt, außer mit -NeuesPasswort).

.EXAMPLE
  Set-ExecutionPolicy -Scope Process Bypass
  .\kissa-tower.ps1                        # Backups nach D:\kissa-backup (oder C:\, wenn es kein D: gibt)
  .\kissa-tower.ps1 -BackupPfad E:\backup
#>
param(
  [string]$BackupPfad = $(if (Test-Path 'D:\') { 'D:\kissa-backup' } else { 'C:\kissa-backup' }),
  [string]$Benutzer = 'kissa',
  [int]$Port = 8000,
  [int]$LeerlaufMinuten = 15,
  [switch]$NeuesPasswort,
  [switch]$Entfernen
)
$ErrorActionPreference = 'Stop'
$RestServerVersion = '0.15.0'
$Dir = 'C:\kissa-tower'

function Ok($t)   { Write-Host "  ✓ $t" -ForegroundColor Green }
function Info($t) { Write-Host "  $t" -ForegroundColor DarkGray }
function Head($t) { Write-Host "`n🐾 $t" -ForegroundColor DarkYellow }

if ($Entfernen) {
  Head 'kissa-Tower entfernen'
  'kissa rest-server', 'kissa auto-shutdown' | ForEach-Object { Unregister-ScheduledTask -TaskName $_ -Confirm:$false -ErrorAction SilentlyContinue }
  Get-Process rest-server -ErrorAction SilentlyContinue | Stop-Process -Force
  Remove-NetFirewallRule -DisplayName 'kissa rest-server' -ErrorAction SilentlyContinue
  Remove-Item $Dir -Recurse -Force -ErrorAction SilentlyContinue
  Ok "Aufgaben, Firewall-Regel und $Dir entfernt. Die Backups in $BackupPfad bleiben liegen."
  return
}

# ---------- 1. rest-server laden und prüfen ----------
Head 'rest-server laden'
New-Item -ItemType Directory -Force -Path $Dir, $BackupPfad | Out-Null
$zip = "rest-server_${RestServerVersion}_windows_amd64.zip"
$base = "https://github.com/restic/rest-server/releases/download/v$RestServerVersion"
$tmp = Join-Path $env:TEMP "kissa-tower"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
Invoke-WebRequest "$base/$zip" -OutFile "$tmp\$zip" -UseBasicParsing
$sums = (Invoke-WebRequest "$base/SHA256SUMS" -UseBasicParsing).Content
$want = ($sums -split "`n" | Where-Object { $_ -match [regex]::Escape($zip) } | Select-Object -First 1) -split '\s+' | Select-Object -First 1
$have = (Get-FileHash "$tmp\$zip" -Algorithm SHA256).Hash
if (-not $want -or $have -ne $want.ToUpper()) { throw "Checksumme passt nicht ($zip) – Abbruch." }
Ok "Checksumme geprüft"
Get-Process rest-server -ErrorAction SilentlyContinue | Stop-Process -Force
Expand-Archive "$tmp\$zip" -DestinationPath $tmp -Force
Copy-Item (Get-ChildItem $tmp -Recurse -Filter rest-server.exe | Select-Object -First 1).FullName "$Dir\rest-server.exe" -Force
Ok "rest-server $RestServerVersion nach $Dir"

# ---------- 2. Zugang (htpasswd) ----------
Head 'Zugang'
$htpasswd = Join-Path $BackupPfad '.htpasswd'
$passwort = $null
if ($NeuesPasswort -or -not (Test-Path $htpasswd)) {
  $chars = [char[]]'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  $bytes = New-Object byte[] 32
  [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
  $passwort = -join ($bytes | ForEach-Object { $chars[$_ % $chars.Length] })
  # {SHA}-Format: SHA-1, Base64 – bei 32 Zufallszeichen nicht knackbar
  $sha = [Security.Cryptography.SHA1]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes($passwort))
  Set-Content -Path $htpasswd -Value "${Benutzer}:{SHA}$([Convert]::ToBase64String($sha))" -Encoding ascii -NoNewline
  Ok 'Neues Passwort erzeugt'
} else {
  Ok 'Passwort bleibt wie bisher (steht in Bitwarden)'
}

# ---------- 3. Dienst beim Systemstart ----------
Head 'Autostart (ohne Anmeldung)'
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
  -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 5 -RestartInterval (New-TimeSpan -Minutes 1) -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
$restArgs = "--path `"$BackupPfad`" --listen :$Port --append-only --private-repos --htpasswd-file `"$htpasswd`""
Register-ScheduledTask -TaskName 'kissa rest-server' -Force -Settings $settings -Principal $principal `
  -Trigger (New-ScheduledTaskTrigger -AtStartup) `
  -Action (New-ScheduledTaskAction -Execute "$Dir\rest-server.exe" -Argument $restArgs) `
  -Description 'kissa: Backup-Empfänger für den Laptop (restic rest-server, append-only)' | Out-Null
Start-ScheduledTask -TaskName 'kissa rest-server'
Ok "rest-server startet bei jedem Hochfahren (Port $Port, append-only)"

# ---------- 4. Auto-Shutdown nach dem Wecken ----------
@"
# kissa auto-shutdown – läuft beim Start als SYSTEM.
# Meldet sich jemand an (explorer läuft), endet das Skript: dann bleibt der PC an.
# Sonst: $LeerlaufMinuten Minuten nach dem letzten Backup-Zugriff herunterfahren.
Start-Sleep -Seconds 120
`$last = Get-Date
while (`$true) {
  if (Get-Process explorer -ErrorAction SilentlyContinue) { exit }
  if (Get-NetTCPConnection -LocalPort $Port -State Established -ErrorAction SilentlyContinue) { `$last = Get-Date }
  if (((Get-Date) - `$last).TotalMinutes -ge $LeerlaufMinuten) {
    shutdown.exe /s /t 60 /c "kissa: Backup fertig – der Tower geht wieder schlafen. (Abbrechen: shutdown /a)"
    exit
  }
  Start-Sleep -Seconds 30
}
"@ | Set-Content -Path "$Dir\auto-shutdown.ps1" -Encoding utf8
Register-ScheduledTask -TaskName 'kissa auto-shutdown' -Force -Settings $settings -Principal $principal `
  -Trigger (New-ScheduledTaskTrigger -AtStartup) `
  -Action (New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Dir\auto-shutdown.ps1`"") `
  -Description 'kissa: fährt den Tower nach einem Backup wieder herunter, wenn niemand angemeldet ist' | Out-Null
Ok "Auto-Shutdown: $LeerlaufMinuten Min. nach dem Backup, nur wenn niemand angemeldet ist"

# ---------- 5. Firewall ----------
Remove-NetFirewallRule -DisplayName 'kissa rest-server' -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName 'kissa rest-server' -Direction Inbound -Protocol TCP -LocalPort $Port `
  -RemoteAddress LocalSubnet -Action Allow -Profile Any | Out-Null
Ok "Firewall: Port $Port nur aus dem Heimnetz"

# ---------- 6. Wake-on-LAN + Schnellstart ----------
Head 'Wake-on-LAN'
$nic = Get-NetAdapter -Physical | Where-Object { $_.Status -eq 'Up' -and $_.MediaType -eq '802.3' } | Select-Object -First 1
if (-not $nic) { throw 'Keine aktive LAN-Verbindung gefunden – Wake-on-LAN braucht das Kabel.' }
try { Enable-NetAdapterPowerManagement -Name $nic.Name -WakeOnMagicPacket -ErrorAction Stop; Ok "Magic Packet an $($nic.Name)" }
catch { Info "Energieverwaltung der Karte nicht änderbar: $($_.Exception.Message)" }
foreach ($kw in '*WakeOnMagicPacket', 'S5WakeOnLan', 'WakeFromPowerOff', 'EnablePME') {
  try { Set-NetAdapterAdvancedProperty -Name $nic.Name -RegistryKeyword $kw -RegistryValue 1 -ErrorAction Stop; Ok "Treiber: $kw" } catch { }
}
Set-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power' -Name HiberbootEnabled -Value 0
Ok 'Windows-Schnellstart aus (sonst wacht der PC aus dem ausgeschalteten Zustand oft nicht auf)'

# ---------- 7. Prüfen + Werte für den Laptop ----------
Start-Sleep -Seconds 2
$ip = (Get-NetIPAddress -InterfaceIndex $nic.ifIndex -AddressFamily IPv4 | Select-Object -First 1).IPAddress
try { Invoke-WebRequest "http://127.0.0.1:$Port/" -UseBasicParsing -TimeoutSec 5 | Out-Null; $up = $true }
catch { $up = [bool]$_.Exception.Response }   # 401 = läuft, will nur ein Passwort
if ($up) { Ok 'rest-server antwortet' } else { Info 'rest-server antwortet (noch) nicht – nach einem Neustart erneut prüfen' }

Head 'Fertig! Auf dem Laptop:  kissa backup einrichten'
Write-Host ''
Write-Host "  Tower-IP   : $ip"
Write-Host "  MAC-Adresse: $($nic.MacAddress)"
Write-Host "  Benutzer   : $Benutzer"
if ($passwort) { Write-Host "  Passwort   : $passwort" -ForegroundColor Yellow; Write-Host '  → Passwort in Bitwarden speichern (Notiz „kissa tower“).' -ForegroundColor Yellow }
Write-Host ''
Info 'Noch von Hand (einmalig):'
Info "  1. EasyBox: dem Tower eine feste IP geben (DHCP-Reservierung für $($nic.MacAddress))"
Info '  2. BIOS/UEFI: „Wake on LAN“ bzw. „Power On by PCI-E“ AN, „ErP“/„EuP“/„Deep Sleep“ AUS'
Info '  3. Keine automatische Windows-Anmeldung – sonst hält der Auto-Shutdown den Tower für „benutzt“'
