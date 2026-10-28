[CmdletBinding()]
param([string]$DocumentsPath)
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'scripts\BalkanTools.psm1') -Force
$stage = $null
try {
    $paths = Get-BalkanPaths $DocumentsPath
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
    $output = Join-Path $PSScriptRoot 'diagnostics'
    New-Item -ItemType Directory -Force -Path $output | Out-Null
    $stage = Join-Path $output ('.collect-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $stage | Out-Null
    $wanted = @('error.log','setup.log','game.log','system.log','exceptions.log','exception.txt','meta.yml')
    $logs = Join-Path $paths.Data 'logs'
    if (Test-Path -LiteralPath $logs) {
        New-Item -ItemType Directory -Path (Join-Path $stage 'logs') | Out-Null
        foreach ($name in $wanted) {
            $file = Join-Path $logs $name
            if (Test-Path -LiteralPath $file -PathType Leaf) {
                # Copy logs only. Never upload a save or memory dump.
                Copy-Item -LiteralPath $file -Destination (Join-Path $stage "logs\$name")
            }
        }
    }
    $crashes = Join-Path $paths.Data 'crashes'
    if (Test-Path -LiteralPath $crashes) {
        $latest = Get-ChildItem -LiteralPath $crashes -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($latest) {
            $crashOut = Join-Path $stage 'latest_crash'
            New-Item -ItemType Directory -Path $crashOut | Out-Null
            $n = 0
            foreach ($file in (Get-ChildItem -LiteralPath $latest.FullName -Recurse -File)) {
                if ($wanted -contains $file.Name -and $file.Length -le (10 * 1024 * 1024)) {
                    $n++
                    Copy-Item -LiteralPath $file.FullName -Destination (Join-Path $crashOut "$n-$($file.Name)")
                }
            }
        }
    }
    foreach ($entry in @(@($paths.LoadFile, 'dlc_load.json'), @((Join-Path $paths.ModDirectory 'Balkan_Collapse\descriptor.mod'), 'installed_descriptor.mod'))) {
        if (Test-Path -LiteralPath $entry[0] -PathType Leaf) { Copy-Item -LiteralPath $entry[0] -Destination (Join-Path $stage $entry[1]) }
    }
    @('Balkan Collapse diagnostic bundle — 2.0.5', "Collected: $(Get-Date -Format o)",
      'No saves, memory dumps, browser data or credentials were collected.',
      'Review before sending: game logs can contain your Windows username, paths and system details.',
      'Please also state HOI4 version, DLC list, selected bookmark, and the last visible loading step.') |
        Set-Content -LiteralPath (Join-Path $stage 'READ_ME.txt') -Encoding UTF8
    $zip = Join-Path $output "Balkan_Collapse_logs-$stamp.zip"
    Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip
    Write-Host "Готово: $zip" -ForegroundColor Green
    Write-Host 'Перед отправкой проверь архив: в логах могут быть имя пользователя Windows, пути и сведения о компьютере.'
} catch {
    Write-Host "ОШИБКА: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    if ($stage -and (Test-Path -LiteralPath $stage)) { Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue }
}
