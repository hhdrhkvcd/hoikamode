[CmdletBinding()]
param([string]$GamePath, [string]$DocumentsPath, [switch]$NoLaunch, [switch]$Yes)
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'scripts\BalkanTools.psm1') -Force
try {
    Assert-BalkanGameStopped
    $paths = Get-BalkanPaths $DocumentsPath
    $repair = $false
    try { $settings = Read-BalkanSettings $paths.LoadFile }
    catch {
        $repair = $true
        $settings = [pscustomobject]@{ enabled_mods = @(); disabled_dlcs = @() }
        Write-Warning 'dlc_load.json повреждён. После подтверждения сохраню исходник и создам новый список без модов; список отключённых DLC тоже будет сброшен.'
    }
    if ($GamePath) { $null = Find-BalkanGame $GamePath }
    Write-Host 'Безопасный запуск чистой HOI4: все моды будут отключены, но не удалены.' -ForegroundColor Cyan
    if (!$Yes -and (Read-Host 'Продолжить? (Y/N)') -notmatch '^(Y|YES|Д|ДА)$') { exit 0 }
    New-Item -ItemType Directory -Force -Path $paths.Data,$paths.Backups | Out-Null
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
    Backup-BalkanSettings $paths $stamp
    $settings.enabled_mods = @()
    $temp = $paths.LoadFile + '.bc-vanilla.tmp'
    Write-BalkanJson $temp $settings
    Move-Item -LiteralPath $temp -Destination $paths.LoadFile -Force
    Write-Host 'Все моды отключены. Если чистая игра тоже не запускается, проверь файлы игры в Steam и собери логи.' -ForegroundColor Green
    Start-BalkanGame -GamePath $GamePath -NoLaunch:$NoLaunch
} catch {
    Write-Host "ОШИБКА: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
