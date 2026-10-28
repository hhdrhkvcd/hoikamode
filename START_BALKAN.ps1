[CmdletBinding()]
param([string]$GamePath, [string]$DocumentsPath, [switch]$NoLaunch, [switch]$Yes)
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'scripts\BalkanTools.psm1') -Force

$stage = $null
$transactionStarted = $false
$oldModMoved = $false
$newModInstalled = $false
$descriptorTouched = $false
$loadTouched = $false
$oldDescriptorExists = $false
$oldLoadExists = $false
try {
    Assert-BalkanGameStopped
    $paths = Get-BalkanPaths $DocumentsPath
    $sourceMod = Join-Path $PSScriptRoot 'Balkan_Collapse'
    $sourceDescriptor = Join-Path $PSScriptRoot 'Balkan_Collapse.mod'
    $payload = Join-Path $PSScriptRoot 'assets\millennium_map.zip'
    $manifest = Join-Path $PSScriptRoot 'assets\MAP_SOURCE.json'
    $flagPayload = Join-Path $PSScriptRoot 'assets/compatibility_flags.zip'
    $flagManifest = Join-Path $PSScriptRoot 'assets/FLAGS_SOURCE.json'
    $targetMod = Join-Path $paths.ModDirectory 'Balkan_Collapse'
    $targetDescriptor = Join-Path $paths.ModDirectory 'Balkan_Collapse.mod'
    if (!(Test-Path -LiteralPath $sourceMod -PathType Container) -or !(Test-Path -LiteralPath $sourceDescriptor -PathType Leaf)) {
        throw 'Не найдены Balkan_Collapse и Balkan_Collapse.mod рядом с BAT. Распакуй ВЕСЬ новый ZIP, не запускай BAT внутри архива.'
    }
    if ([IO.Path]::GetFullPath($sourceMod).TrimEnd('\') -eq [IO.Path]::GetFullPath($targetMod).TrimEnd('\')) {
        throw 'Нельзя устанавливать мод поверх папки, из которой работает установщик. Распакуй ZIP в отдельную папку, например на рабочий стол.'
    }
    $sourceHasMap = Test-Path -LiteralPath (Join-Path $sourceMod 'map\provinces.bmp') -PathType Leaf
    if (!$sourceHasMap -and !(Test-Path -LiteralPath $payload -PathType Leaf)) {
        throw 'Нет данных карты. Нужен целый новый Balkan_Collapse_1980.zip или assets\millennium_map.zip из GitHub. Старый ZIP 1.6 не подходит.'
    }
    # Parse BEFORE modifying the installed mod. Malformed JSON is never overwritten.
    $settings = Read-BalkanSettings $paths.LoadFile
    if ($GamePath) { $null = Find-BalkanGame $GamePath }
    Write-Host 'Balkan Collapse 2.0.3 — современная карта, 1980 / 2008' -ForegroundColor Cyan
    Write-Host "Данные игры: $($paths.Data)"
    Write-Host 'Будет включён ТОЛЬКО Balkan Collapse. DLC сохраняются. Полный Millennium Dawn включать одновременно нельзя.'
    Write-Host 'Старая версия мода и список модов будут сохранены. Сохранения, настройки и файлы игры не удаляются.'
    if (!$Yes) {
        $answer = Read-Host 'Установить? (Y/N)'
        if ($answer -notmatch '^(Y|YES|Д|ДА)$') { Write-Host 'Отменено. Ничего не изменено.'; exit 0 }
    }
    New-Item -ItemType Directory -Force -Path $paths.ModDirectory,$paths.Backups | Out-Null
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
    $stage = Join-Path $paths.Backups ('.staging-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $stage | Out-Null
    $stagedMod = Join-Path $stage 'Balkan_Collapse'
    Copy-Item -LiteralPath $sourceMod -Destination $stagedMod -Recurse
    # A ZIP extracted over an old source folder can retain this fatal early override.
    # Remove only our known obsolete file from the staging copy, never from the source/game.
    $obsoleteDefine = Join-Path $stagedMod 'common\defines\00_balkan_collapse.lua'
    if (Test-Path -LiteralPath $obsoleteDefine -PathType Leaf) {
        Remove-Item -LiteralPath $obsoleteDefine -Force
        Write-Warning 'Убрана устаревшая ранняя Lua-настройка из устанавливаемой копии.'
    }
    if (!(Test-Path -LiteralPath $manifest -PathType Leaf) -or !(Test-Path -LiteralPath $flagManifest -PathType Leaf)) {
        throw 'Неполная сборка: отсутствуют данные проверки карты или флагов. Распакуй весь новый ZIP.'
    }
    $mapInfo = Get-Content -LiteralPath $manifest -Raw -Encoding UTF8 | ConvertFrom-Json
    $flagInfo = Get-Content -LiteralPath $flagManifest -Raw -Encoding UTF8 | ConvertFrom-Json
    if (Test-Path -LiteralPath $payload -PathType Leaf) {
        if (!(Test-Path -LiteralPath $manifest -PathType Leaf)) { throw 'Нет assets\MAP_SOURCE.json для проверки архива карты.' }
        $actualHash = (Get-FileHash -LiteralPath $payload -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actualHash -ne $mapInfo.payload_sha256) { throw 'Контрольная сумма архива карты не совпадает. Скачай архив заново.' }
        Write-Host 'Распаковываю карту из GitHub...' -ForegroundColor Cyan
        Expand-Archive -LiteralPath $payload -DestinationPath $stagedMod -Force
    }
    if (Test-Path -LiteralPath $flagPayload -PathType Leaf) {
        $actualHash = (Get-FileHash -LiteralPath $flagPayload -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actualHash -ne $flagInfo.payload_sha256) { throw 'Повреждён исходный архив совместимости флагов.' }
        Expand-Archive -LiteralPath $flagPayload -DestinationPath $stagedMod -Force
    }
    foreach ($member in $flagInfo.payload_files.PSObject.Properties) {
        if (!(Test-Path -LiteralPath (Join-Path $stagedMod $member.Name) -PathType Leaf)) {
            throw "Неполная сборка флагов: $($member.Name). Распакуй весь новый ZIP."
        }
    }
    $placementFile = Join-Path $stagedMod 'map/buildings.txt'
    $stackFile = Join-Path $stagedMod 'map/unitstacks.txt'
    $placementHash = (Get-FileHash -LiteralPath $placementFile -Algorithm SHA256).Hash.ToLowerInvariant()
    $stackHash = (Get-FileHash -LiteralPath $stackFile -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($placementHash -ne $mapInfo.geometry.building_positions_sha256 -or $stackHash -ne $mapInfo.payload_files.'map/unitstacks.txt') {
        throw 'В папке смешаны старые и новые данные размещения карты. Распакуй новый ZIP в пустую папку.'
    }
    $portCount = @(Select-String -LiteralPath $placementFile -Pattern ';naval_base_spawn;').Count
    if ($portCount -ne $mapInfo.geometry.ports.Count) { throw 'В карте не хватает точек портов. Установка отменена.' }
    Write-Host "Проверены точки портов: $portCount. Проверены файлы совместимости флагов." -ForegroundColor Cyan
    foreach ($required in @('common\defines\zz_balkan_collapse.lua','map\provinces.bmp','map\definition.csv','map\rivers.bmp','map\heightmap.bmp','map\terrain_morecities.bmp','map\trees.bmp','map\supply_nodes.txt','history\states\107-BC.txt','descriptor.mod')) {
        if (!(Test-Path -LiteralPath (Join-Path $stagedMod $required) -PathType Leaf)) { throw "Неполная сборка: $required" }
    }
    $stateFiles = @(Get-ChildItem -LiteralPath (Join-Path $stagedMod 'history\states') -Filter '*.txt' -File)
    if ($stateFiles.Count -ne 1493) { throw "Ожидалось 1493 области карты, найдено $($stateFiles.Count). Установка отменена." }
    $oldModBackup = Join-Path $paths.Backups "Balkan_Collapse-$stamp"
    $oldDescriptorBackup = Join-Path $paths.Backups "Balkan_Collapse-$stamp.mod"
    $oldLoadExists = Test-Path -LiteralPath $paths.LoadFile -PathType Leaf
    $oldDescriptorExists = Test-Path -LiteralPath $targetDescriptor -PathType Leaf
    Backup-BalkanSettings $paths $stamp
    if ($oldDescriptorExists) { Copy-Item -LiteralPath $targetDescriptor -Destination $oldDescriptorBackup }
    $settings.enabled_mods = @('mod/Balkan_Collapse.mod')
    $stagedLoad = Join-Path $stage 'dlc_load.json'
    Write-BalkanJson $stagedLoad $settings
    $null = Read-BalkanSettings $stagedLoad
    Write-BalkanJson (Join-Path $paths.Backups "transaction-$stamp.json") ([pscustomobject]@{
        version = '2.0.3'; previous_load_existed = $oldLoadExists
        previous_descriptor_existed = $oldDescriptorExists; target = $targetMod
    })
    # Transaction: only now replace an existing install, after all staging checks succeeded.
    $transactionStarted = $true
    if (Test-Path -LiteralPath $targetMod) {
        Move-Item -LiteralPath $targetMod -Destination $oldModBackup
        $oldModMoved = $true
    }
    Move-Item -LiteralPath $stagedMod -Destination $targetMod
    $newModInstalled = $true
    $descriptorTouched = $true
    Copy-Item -LiteralPath $sourceDescriptor -Destination $targetDescriptor -Force
    $loadTouched = $true
    Copy-Item -LiteralPath $stagedLoad -Destination $paths.LoadFile -Force
    $transactionStarted = $false
    Write-Host 'Мод 2.0.3 установлен. Доступны сценарии 1980 и 2008.' -ForegroundColor Green
    Write-Host "Резервные копии: $($paths.Backups)"
    Write-Host 'Используй НОВУЮ игру: сохранения прежней карты несовместимы.'
} catch {
    $failure = $_.Exception.Message
    if ($transactionStarted) {
        Write-Warning 'Установка не завершена. Восстанавливаю прежние файлы...'
        try {
            if ($newModInstalled -and (Test-Path -LiteralPath $targetMod)) { Remove-Item -LiteralPath $targetMod -Recurse -Force }
            if ($oldModMoved) { Move-Item -LiteralPath $oldModBackup -Destination $targetMod }
            if ($descriptorTouched) {
                if ($oldDescriptorExists) { Copy-Item -LiteralPath $oldDescriptorBackup -Destination $targetDescriptor -Force }
                elseif (Test-Path -LiteralPath $targetDescriptor) { Remove-Item -LiteralPath $targetDescriptor -Force }
            }
            if ($loadTouched) {
                if ($oldLoadExists) { Copy-Item -LiteralPath (Join-Path $paths.Backups "dlc_load-$stamp.json") -Destination $paths.LoadFile -Force }
                elseif (Test-Path -LiteralPath $paths.LoadFile) { Remove-Item -LiteralPath $paths.LoadFile -Force }
            }
        } catch { Write-Warning "Автооткат не завершён: $($_.Exception.Message). Резервные копии: $($paths.Backups)" }
    }
    Write-Host "ОШИБКА: $failure" -ForegroundColor Red
    exit 1
} finally {
    if ($stage -and (Test-Path -LiteralPath $stage)) { Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue }
}
# A launch failure must not roll back a successfully installed mod.
try { Start-BalkanGame -GamePath $GamePath -NoLaunch:$NoLaunch }
catch { Write-Warning "Мод установлен, но игра не запущена: $($_.Exception.Message)"; exit 1 }
