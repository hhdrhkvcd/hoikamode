Set-StrictMode -Version 2.0

function Get-BalkanPaths([string]$DocumentsPath) {
    if ([string]::IsNullOrWhiteSpace($DocumentsPath)) {
        $DocumentsPath = [Environment]::GetFolderPath('MyDocuments')
    }
    if ([string]::IsNullOrWhiteSpace($DocumentsPath)) { throw 'Не удалось определить папку Документы.' }
    $data = Join-Path ([IO.Path]::GetFullPath($DocumentsPath)) 'Paradox Interactive\Hearts of Iron IV'
    [pscustomobject]@{
        Data = $data
        ModDirectory = (Join-Path $data 'mod')
        Backups = (Join-Path $data 'Balkan_Collapse_backups')
        LoadFile = (Join-Path $data 'dlc_load.json')
    }
}

function Assert-BalkanGameStopped {
    $running = @(Get-Process -Name 'hoi4','dowser','Paradox Launcher','Paradox Launcher v2' -ErrorAction SilentlyContinue)
    if ($running.Count -gt 0) { throw 'Сначала закрой HOI4 и Paradox Launcher. Файлы не изменены.' }
}

function Read-BalkanSettings([string]$Path) {
    if (Test-Path -LiteralPath $Path) {
        try { $settings = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json -ErrorAction Stop }
        catch { throw "Повреждён dlc_load.json: $Path. Он НЕ перезаписан. Сохрани его копию и проверь JSON." }
        if ($null -eq $settings -or $settings -isnot [pscustomobject]) { throw 'dlc_load.json должен содержать JSON-объект. Он НЕ перезаписан.' }
    } else { $settings = [pscustomobject]@{} }
    foreach ($key in @('enabled_mods','disabled_dlcs')) {
        if (@($settings.PSObject.Properties | ForEach-Object { $_.Name }) -notcontains $key) {
            $settings | Add-Member -MemberType NoteProperty -Name $key -Value @()
        }
    }
    return $settings
}

function Write-BalkanJson([string]$Path, $Object) {
    $utf8 = [Text.UTF8Encoding]::new($false)
    [IO.File]::WriteAllText($Path, ($Object | ConvertTo-Json -Depth 30), $utf8)
}

function Backup-BalkanSettings($Paths, [string]$Stamp) {
    New-Item -ItemType Directory -Path $Paths.Backups -Force | Out-Null
    if (Test-Path -LiteralPath $Paths.LoadFile) {
        Copy-Item -LiteralPath $Paths.LoadFile -Destination (Join-Path $Paths.Backups "dlc_load-$Stamp.json")
    } else {
        Write-BalkanJson (Join-Path $Paths.Backups "dlc_load-$Stamp.json") ([pscustomobject]@{ enabled_mods = @(); disabled_dlcs = @() })
    }
}

function Find-BalkanGame([string]$GamePath) {
    if (![string]::IsNullOrWhiteSpace($GamePath)) {
        if (Test-Path -LiteralPath $GamePath -PathType Container) { $GamePath = Join-Path $GamePath 'hoi4.exe' }
        if (!(Test-Path -LiteralPath $GamePath -PathType Leaf)) { throw "Не найден hoi4.exe: $GamePath" }
        return [IO.Path]::GetFullPath($GamePath)
    }
    $roots = @()
    foreach ($reg in @('HKCU:\Software\Valve\Steam','HKLM:\SOFTWARE\WOW6432Node\Valve\Steam')) {
        try {
            $item = Get-ItemProperty -Path $reg -ErrorAction Stop
            foreach ($key in @('SteamPath','InstallPath')) {
                if ($item.PSObject.Properties.Name -contains $key -and $item.$key) { $roots += $item.$key }
            }
        } catch { }
    }
    foreach ($dir in @($env:ProgramFiles, ${env:ProgramFiles(x86)})) {
        if ($dir) { $roots += (Join-Path $dir 'Steam') }
    }
    $libraries = @($roots)
    foreach ($root in ($roots | Select-Object -Unique)) {
        $vdf = Join-Path $root 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf) {
            $contents = Get-Content -LiteralPath $vdf -Raw -Encoding UTF8
            foreach ($match in [regex]::Matches($contents, '"path"\s+"([^"]+)"')) {
                $libraries += $match.Groups[1].Value.Replace('\\','\')
            }
        }
    }
    foreach ($library in ($libraries | Select-Object -Unique)) {
        $exe = Join-Path $library 'steamapps\common\Hearts of Iron IV\hoi4.exe'
        if (Test-Path -LiteralPath $exe -PathType Leaf) { return $exe }
    }
    return $null
}

function Start-BalkanGame([string]$GamePath, [switch]$NoLaunch) {
    if ($NoLaunch) { return }
    $exe = Find-BalkanGame $GamePath
    if (!$exe) {
        Write-Warning 'hoi4.exe не найден автоматически. Установка сохранена; автоматического запуска через лаунчер не будет, чтобы он не заменил набор модов.'
        Write-Host 'Укажи путь: powershell -File .\START_BALKAN.ps1 -GamePath "D:\SteamLibrary\steamapps\common\Hearts of Iron IV\hoi4.exe"'
        return
    }
    Write-Host 'Проверочный запуск HOI4 с -debug. Файлы самой игры не изменяются.' -ForegroundColor Cyan
    Start-Process -FilePath $exe -WorkingDirectory (Split-Path -Parent $exe) -ArgumentList @('-debug')
}

Export-ModuleMember -Function @('Get-BalkanPaths', 'Assert-BalkanGameStopped', 'Read-BalkanSettings', 'Write-BalkanJson', 'Backup-BalkanSettings', 'Find-BalkanGame', 'Start-BalkanGame')
