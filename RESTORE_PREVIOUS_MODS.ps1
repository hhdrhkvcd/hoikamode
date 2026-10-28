[CmdletBinding()]
param([string]$DocumentsPath, [switch]$Yes)
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'scripts\BalkanTools.psm1') -Force
try {
    Assert-BalkanGameStopped
    $paths = Get-BalkanPaths $DocumentsPath
    if (!(Test-Path -LiteralPath $paths.Backups)) { throw 'Нет папки резервных копий.' }
    $backup = Get-ChildItem -LiteralPath $paths.Backups -Filter 'dlc_load-*.json' -File |
        Sort-Object Name -Descending | Select-Object -First 1
    if (!$backup) { throw 'Нет резервной копии списка модов.' }
    $null = Read-BalkanSettings $backup.FullName
    Write-Host "Будет восстановлен список из $($backup.Name). Старые моды из него снова включатся."
    Write-Host 'Для запуска БЕЗ модов вместо этого используй START_VANILLA.bat.' -ForegroundColor Yellow
    if (!$Yes -and (Read-Host 'Восстановить список? (Y/N)') -notmatch '^(Y|YES|Д|ДА)$') { exit 0 }
    if (Test-Path -LiteralPath $paths.LoadFile) {
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
        Copy-Item -LiteralPath $paths.LoadFile -Destination (Join-Path $paths.Backups "before-restore-$stamp.json")
    }
    $temp = $paths.LoadFile + '.bc-restore.tmp'
    Copy-Item -LiteralPath $backup.FullName -Destination $temp -Force
    Move-Item -LiteralPath $temp -Destination $paths.LoadFile -Force
    Write-Host 'Прежний список восстановлен. Папки модов, сохранения и файлы игры не изменены.' -ForegroundColor Green
} catch {
    Write-Host "ОШИБКА: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
