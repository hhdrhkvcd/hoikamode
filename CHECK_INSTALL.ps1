[CmdletBinding()]
param([string]$DocumentsPath)
$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot 'scripts\BalkanTools.psm1') -Force

function Get-Digest([string]$Path) {
    if (!(Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

try {
    $paths = Get-BalkanPaths $DocumentsPath
    $installed = Join-Path $paths.ModDirectory 'Balkan_Collapse'
    $problems = New-Object Collections.Generic.List[string]
    Write-Host 'Проверка УСТАНОВЛЕННОЙ копии Balkan Collapse (не папки ZIP)' -ForegroundColor Cyan
    Write-Host "Папка игры: $($paths.Data)"

    $descriptor = Join-Path $installed 'descriptor.mod'
    if (!(Test-Path -LiteralPath $installed -PathType Container) -or !(Test-Path -LiteralPath $descriptor -PathType Leaf)) {
        throw "Мод ещё не установлен: нет $installed. Сначала запусти START_BALKAN.bat."
    }
    $version = ([regex]::Match((Get-Content -LiteralPath $descriptor -Raw -Encoding UTF8), 'version\s*=\s*"([^"]+)"')).Groups[1].Value
    Write-Host "Версия установленного мода: $version"
    if ($version -ne '2.0.5') { $problems.Add("Ожидалась версия 2.0.5, найдена '$version'.") }

    $early = Join-Path $installed 'common\defines\00_balkan_collapse.lua'
    if (Test-Path -LiteralPath $early) { $problems.Add('Осталcя устаревший common\defines\00_balkan_collapse.lua.') }
    if (!(Test-Path -LiteralPath (Join-Path $installed 'common\defines\zz_balkan_collapse.lua'))) { $problems.Add('Нет common\defines\zz_balkan_collapse.lua.') }

    $placement = Join-Path $installed 'map\buildings.txt'
    if (!(Test-Path -LiteralPath $placement -PathType Leaf)) {
        $problems.Add('Нет map\buildings.txt — карта не распакована.')
    } else {
        $ports = @(Select-String -LiteralPath $placement -Pattern ';naval_base_spawn;').Count
        Write-Host "Точек портов в установленной карте: $ports (нужно 2485)"
        if ($ports -ne 2485) { $problems.Add("Точек портов $ports вместо 2485 — это старая карта 2.0.2 и ниже.") }
        $bytes = [IO.File]::ReadAllBytes($placement)
        if ($bytes.Length -gt 0 -and $bytes[$bytes.Length - 1] -eq 10) { $problems.Add('В buildings.txt осталась пустая конечная запись.') }
    }

    $definition = Join-Path $installed 'map\definition.csv'
    if (Test-Path -LiteralPath $definition -PathType Leaf) {
        $provinces = @((Get-Content -LiteralPath $definition -Encoding UTF8) | Where-Object { $_ -match '^\d+;' }).Count
        Write-Host "Провинций в definition.csv: $provinces (нужно 14980)"
        if ($provinces -ne 14980) { $problems.Add("Провинций $provinces вместо 14980 — установлена старая карта без исправления микропровинций.") }
    }

    foreach ($mapFile in @('map\provinces.bmp','map\unitstacks.txt','map\definition.csv')) {
        if (!(Test-Path -LiteralPath (Join-Path $installed $mapFile) -PathType Leaf)) { $problems.Add("Нет $mapFile.") }
    }

    $manifest = Join-Path $PSScriptRoot 'assets\MAP_SOURCE.json'
    if (Test-Path -LiteralPath $manifest -PathType Leaf) {
        $mapInfo = Get-Content -LiteralPath $manifest -Raw -Encoding UTF8 | ConvertFrom-Json
        $placementHash = Get-Digest $placement
        if ($placementHash -and $placementHash -ne $mapInfo.geometry.building_positions_sha256) {
            $problems.Add('map\buildings.txt не совпадает с проверенным размещением из ZIP.')
        }
        $stackHash = Get-Digest (Join-Path $installed 'map\unitstacks.txt')
        if ($stackHash -and $stackHash -ne $mapInfo.payload_files.'map/unitstacks.txt') {
            $problems.Add('map\unitstacks.txt не совпадает с исправленным.')
        }
    } else { $problems.Add('Рядом с BAT нет assets\MAP_SOURCE.json: ZIP распакован не полностью.') }

    $flagManifest = Join-Path $PSScriptRoot 'assets\FLAGS_SOURCE.json'
    if (Test-Path -LiteralPath $flagManifest -PathType Leaf) {
        $flagInfo = Get-Content -LiteralPath $flagManifest -Raw -Encoding UTF8 | ConvertFrom-Json
        $missing = 0
        foreach ($member in $flagInfo.payload_files.PSObject.Properties) {
            if (!(Test-Path -LiteralPath (Join-Path $installed $member.Name) -PathType Leaf)) { $missing++ }
        }
        Write-Host "Файлов совместимости флагов: $($flagInfo.payload_files.PSObject.Properties.Count), отсутствует $missing"
        if ($missing -gt 0) { $problems.Add("Не хватает $missing флаговых файлов.") }
    } else { $problems.Add('Рядом с BAT нет assets\FLAGS_SOURCE.json.') }

    $stateCount = @(Get-ChildItem -LiteralPath (Join-Path $installed 'history\states') -Filter '*.txt' -File -ErrorAction SilentlyContinue).Count
    if ($stateCount -ne 1483) { $problems.Add("Областей $stateCount вместо 1483.") }

    if (Test-Path -LiteralPath $paths.LoadFile -PathType Leaf) {
        try {
            $load = Get-Content -LiteralPath $paths.LoadFile -Raw -Encoding UTF8 | ConvertFrom-Json
            $enabled = @($load.enabled_mods | Where-Object { $_ })
            Write-Host "Включённые моды в dlc_load.json: $($enabled -join ', ')"
            $foreign = @($enabled | Where-Object { $_ -ne 'mod/Balkan_Collapse.mod' })
            if ($foreign.Count -gt 0) { $problems.Add("Включены посторонние моды: $($foreign -join ', '). Это частая причина вылета.") }
        } catch { $problems.Add("dlc_load.json не читается как JSON: $($_.Exception.Message)") }
    }

    $logs = Join-Path $paths.Data 'logs'
    foreach ($name in @('error.log','exception.txt')) {
        $file = Join-Path $logs $name
        if (Test-Path -LiteralPath $file -PathType Leaf) {
            Write-Host ("{0}: изменён {1}" -f $name, (Get-Item -LiteralPath $file).LastWriteTime)
        }
    }

    Write-Host ''
    if ($problems.Count -eq 0) {
        Write-Host "Проверка пройдена: в игре установлена корректная сборка $version." -ForegroundColor Green
        Write-Host 'Если она всё ещё вылетает — пришли свежий ZIP из diagnostics/, созданный ПОСЛЕ этого запуска.'
    } else {
        Write-Host 'Найдены расхождения установленной копии:' -ForegroundColor Yellow
        foreach ($problem in $problems) { Write-Host " - $problem" }
        Write-Host ''
        Write-Host 'Исправление: закрой игру и Launcher, распакуй новый ZIP в ПУСТУЮ папку и снова запусти START_BALKAN.bat.' -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "ОШИБКА ПРОВЕРКИ: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
