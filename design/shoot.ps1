param(
  [Parameter(Mandatory=$true)][string]$File,
  [Parameter(Mandatory=$true)][string]$Out,
  [int]$W = 1600,
  [int]$H = 1000
)
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$profile = Join-Path $env:TEMP ('trace-shot-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $profile | Out-Null
$path = $File
$query = ''
$qi = $File.IndexOf('?')
if ($qi -ge 0) { $path = $File.Substring(0, $qi); $query = $File.Substring($qi) }
$abs = (Resolve-Path $path).Path
$outPath = [System.IO.Path]::GetFullPath($Out)
$outDir = Split-Path $outPath -Parent
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
& $edge --headless=new --disable-gpu --hide-scrollbars --no-first-run `
  --user-data-dir="$profile" --window-size="$W,$H" --force-device-scale-factor=1 `
  --virtual-time-budget=5500 --screenshot="$outPath" ("file:///" + $abs.Replace('\','/') + $query) 2>&1 | Out-Null
Start-Sleep -Milliseconds 700
Remove-Item -Recurse -Force $profile -ErrorAction SilentlyContinue
if (Test-Path $outPath) {
  $item = Get-Item $outPath
  "OK $($item.Length) bytes -> $outPath"
} else {
  "FAILED: $outPath"
  exit 1
}
