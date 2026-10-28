# Windows-only integration checks. Uses isolated temporary Documents, never starts HOI4.
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
if ($env:OS -ne 'Windows_NT') { throw 'This test requires Windows PowerShell.' }
$repo = Split-Path -Parent $PSScriptRoot
$shell = (Get-Command powershell.exe -ErrorAction Stop).Source
$work = Join-Path $env:TEMP ('bc-installer-test-' + [guid]::NewGuid().ToString('N'))
$docs = Join-Path $work 'Documents with spaces'
$data = Join-Path $docs 'Paradox Interactive\Hearts of Iron IV'
$load = Join-Path $data 'dlc_load.json'
$target = Join-Path $data 'mod\Balkan_Collapse'
$descriptor = Join-Path $data 'mod\Balkan_Collapse.mod'
$diagnostic = $null
$utf8 = [Text.UTF8Encoding]::new($false)
function Assert-Test([bool]$Value, [string]$Message) { if (!$Value) { throw $Message } }
function Invoke-Check([string]$Name, [int]$Expected, [string[]]$Options = @()) {
    & $shell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $repo $Name) -DocumentsPath $docs @Options | Out-Host
    Assert-Test ($LASTEXITCODE -eq $Expected) "$Name returned $LASTEXITCODE; expected $Expected"
}
try {
    New-Item -ItemType Directory -Path $data -Force | Out-Null
    [IO.File]::WriteAllText($load, '{"enabled_mods":["mod/old.mod"],"disabled_dlcs":["dlc/test.dlc"],"custom_setting":"preserve me"}', $utf8)
    Invoke-Check 'START_BALKAN.ps1' 0 @('-NoLaunch','-Yes')
    $settings = Get-Content -LiteralPath $load -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Test (@($settings.enabled_mods).Count -eq 1 -and $settings.enabled_mods[0] -eq 'mod/Balkan_Collapse.mod') 'Wrong active mods'
    Assert-Test ($settings.disabled_dlcs[0] -eq 'dlc/test.dlc' -and $settings.custom_setting -eq 'preserve me') 'DLC/custom settings were lost'
    Assert-Test ((Get-ChildItem -LiteralPath (Join-Path $target 'history\states') -Filter '*.txt' -File).Count -eq 1493) 'Missing states'
    Assert-Test (Test-Path -LiteralPath (Join-Path $target 'map\provinces.bmp')) 'Map was not expanded'
    Assert-Test (Test-Path -LiteralPath (Join-Path $target 'gfx/flags/A24.tga')) 'Compatibility flags were not expanded'
    Assert-Test (@(Select-String -LiteralPath (Join-Path $target 'map/buildings.txt') -Pattern ';naval_base_spawn;').Count -eq 2496) 'Native port markers missing'
    [IO.File]::WriteAllText((Join-Path $target 'stale.marker'), 'old version', $utf8)
    Invoke-Check 'START_BALKAN.ps1' 0 @('-NoLaunch','-Yes')
    Assert-Test (!(Test-Path -LiteralPath (Join-Path $target 'stale.marker'))) 'Old files survived a clean replacement'
    $backups = Join-Path $data 'Balkan_Collapse_backups'
    Assert-Test (@(Get-ChildItem -LiteralPath $backups -Filter 'stale.marker' -Recurse -File).Count -eq 1) 'Old version was not backed up'

    # Simulate extracting 2.0.3 over old sources, without changing the real repository.
    $overlay = Join-Path $work 'source-overlay'
    New-Item -ItemType Directory -Path $overlay -Force | Out-Null
    foreach ($name in @('Balkan_Collapse','Balkan_Collapse.mod','START_BALKAN.ps1','scripts')) {
        Copy-Item -LiteralPath (Join-Path $repo $name) -Destination $overlay -Recurse
    }
    $overlayAssets = Join-Path $overlay 'assets'
    New-Item -ItemType Directory -Path $overlayAssets | Out-Null
    foreach ($name in @('millennium_map.zip','MAP_SOURCE.json','compatibility_flags.zip','FLAGS_SOURCE.json')) {
        Copy-Item -LiteralPath (Join-Path $repo "assets\$name") -Destination $overlayAssets
    }
    $legacy = Join-Path $overlay 'Balkan_Collapse\common\defines\00_balkan_collapse.lua'
    [IO.File]::WriteAllText($legacy, 'NDefines.NGame.START_DATE = "1936.1.1.12"', $utf8)
    & $shell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $overlay 'START_BALKAN.ps1') -DocumentsPath $docs -NoLaunch -Yes | Out-Host
    Assert-Test ($LASTEXITCODE -eq 0) 'Overlay-source install failed'
    Assert-Test (Test-Path -LiteralPath $legacy) 'Installer modified the source folder'
    Assert-Test (!(Test-Path -LiteralPath (Join-Path $target 'common\defines\00_balkan_collapse.lua'))) 'Obsolete early Lua override survived staging'
    Assert-Test (Test-Path -LiteralPath (Join-Path $target 'common\defines\zz_balkan_collapse.lua')) 'Late Lua override missing'

    $goodLoad = Get-Content -LiteralPath $load -Raw -Encoding UTF8
    $goodDescriptor = (Get-FileHash -LiteralPath $descriptor -Algorithm SHA256).Hash
    [IO.File]::WriteAllText($load, '{ broken json', $utf8)
    Invoke-Check 'START_BALKAN.ps1' 1 @('-NoLaunch','-Yes')
    Assert-Test ((Get-Content -LiteralPath $load -Raw -Encoding UTF8) -eq '{ broken json') 'Malformed settings were overwritten by installer'
    Assert-Test ((Get-FileHash -LiteralPath $descriptor -Algorithm SHA256).Hash -eq $goodDescriptor) 'Installation changed after JSON failure'
    [IO.File]::WriteAllText($load, $goodLoad, $utf8)

    # Lock only the descriptor for writing. Staging/backup reads can still succeed.
    [IO.File]::WriteAllText((Join-Path $target 'rollback.marker'), 'must survive rollback', $utf8)
    $lock = [IO.File]::Open($descriptor, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try { Invoke-Check 'START_BALKAN.ps1' 1 @('-NoLaunch','-Yes') }
    finally { $lock.Dispose() }
    Assert-Test (Test-Path -LiteralPath (Join-Path $target 'rollback.marker')) 'Old mod was lost after replacement failure'
    Assert-Test ((Get-Content -LiteralPath $load -Raw -Encoding UTF8) -eq $goodLoad) 'Playset was changed after replacement failure'

    Invoke-Check 'START_VANILLA.ps1' 0 @('-NoLaunch','-Yes')
    $settings = Get-Content -LiteralPath $load -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Test (@($settings.enabled_mods).Count -eq 0) 'Vanilla mode still enabled a mod'
    Assert-Test ($settings.disabled_dlcs[0] -eq 'dlc/test.dlc') 'Vanilla mode lost DLC settings'
    Assert-Test (Test-Path -LiteralPath $target) 'Vanilla mode deleted the mod'
    Invoke-Check 'RESTORE_PREVIOUS_MODS.ps1' 0 @('-Yes')
    $settings = Get-Content -LiteralPath $load -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Test ($settings.enabled_mods[0] -eq 'mod/Balkan_Collapse.mod') 'Restore did not restore playset'

    [IO.File]::WriteAllText($load, '{ broken again', $utf8)
    Invoke-Check 'START_VANILLA.ps1' 0 @('-NoLaunch','-Yes')
    Assert-Test (@((Get-Content -LiteralPath $load -Raw -Encoding UTF8 | ConvertFrom-Json).enabled_mods).Count -eq 0) 'Confirmed JSON recovery failed'
    Invoke-Check 'RESTORE_PREVIOUS_MODS.ps1' 1 @('-Yes')
    Assert-Test (@((Get-Content -LiteralPath $load -Raw -Encoding UTF8 | ConvertFrom-Json).enabled_mods).Count -eq 0) 'Invalid backup overwrote valid settings'

    $logs = Join-Path $data 'logs'
    $crash = Join-Path $data 'crashes\fake-crash'
    New-Item -ItemType Directory -Path $logs,$crash -Force | Out-Null
    [IO.File]::WriteAllText((Join-Path $logs 'error.log'), 'Fixture log only.', $utf8)
    [IO.File]::WriteAllText((Join-Path $crash 'error.log'), 'Fixture crash only.', $utf8)
    [IO.File]::WriteAllText((Join-Path $crash 'memory.dmp'), 'Do not collect.', $utf8)
    [IO.File]::WriteAllText((Join-Path $crash 'private.hoi4'), 'Do not collect.', $utf8)
    $before = @(Get-ChildItem -Path (Join-Path $repo 'diagnostics\*.zip') -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
    Invoke-Check 'COLLECT_BALKAN_LOGS.ps1' 0
    $new = @(Get-ChildItem -Path (Join-Path $repo 'diagnostics\*.zip') | Where-Object { $before -notcontains $_.FullName })
    Assert-Test ($new.Count -eq 1) 'Diagnostic archive not created'
    $diagnostic = $new[0].FullName
    $unpacked = Join-Path $work 'diagnostic-check'
    Expand-Archive -LiteralPath $diagnostic -DestinationPath $unpacked
    Assert-Test (Test-Path -LiteralPath (Join-Path $unpacked 'logs\error.log')) 'Missing diagnostic log'
    Assert-Test (@(Get-ChildItem -LiteralPath $unpacked -Recurse -File | Where-Object { $_.Extension -in @('.dmp','.hoi4') }).Count -eq 0) 'Private dump/save was collected'
    Write-Host 'Installer integration checks passed; actual HOI4 was NOT launched.' -ForegroundColor Green
} finally {
    if ($diagnostic -and (Test-Path -LiteralPath $diagnostic)) { Remove-Item -LiteralPath $diagnostic -Force }
    if (Test-Path -LiteralPath $work) { Remove-Item -LiteralPath $work -Recurse -Force }
}
