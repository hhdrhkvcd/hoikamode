$ErrorActionPreference = 'Stop'

function Stop-WithMessage([string]$Message) {
    Write-Host "`nОШИБКА: $Message" -ForegroundColor Red
    exit 1
}

$sourceRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceMod = Join-Path $sourceRoot 'Balkan_Collapse'
$sourceDescriptor = Join-Path $sourceRoot 'Balkan_Collapse.mod'
if (!(Test-Path -LiteralPath $sourceMod -PathType Container)) {
    Stop-WithMessage 'рядом со START_BALKAN.bat не найдена папка Balkan_Collapse. Сначала распакуй весь ZIP.'
}
if (!(Test-Path -LiteralPath $sourceDescriptor -PathType Leaf)) {
    Stop-WithMessage 'рядом со START_BALKAN.bat не найден файл Balkan_Collapse.mod. Сначала распакуй весь ZIP.'
}

$documents = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::MyDocuments)
if ([string]::IsNullOrWhiteSpace($documents)) {
    Stop-WithMessage 'Windows не смогла определить папку Документы.'
}
$hoiData = Join-Path $documents 'Paradox Interactive\Hearts of Iron IV'
$modDirectory = Join-Path $hoiData 'mod'
$backupDirectory = Join-Path $hoiData 'Balkan_Collapse_backups'
New-Item -ItemType Directory -Force -Path $modDirectory | Out-Null
New-Item -ItemType Directory -Force -Path $backupDirectory | Out-Null

Write-Host 'Установщик Balkan Collapse' -ForegroundColor Cyan
Write-Host "Папка игры: $hoiData"
Write-Host 'Для надёжной проверки будут временно включены только файлы этого мода.'
Write-Host 'Текущий список модов и предыдущая копия Balkan_Collapse сохранятся в резервной папке.'
$answer = Read-Host 'Продолжить? (Y/N)'
if ($answer -notmatch '^(Y|Д|ДА|YES)$') {
    Write-Host 'Отменено. Ничего не изменено.'
    exit 0
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$targetMod = Join-Path $modDirectory 'Balkan_Collapse'
$targetDescriptor = Join-Path $modDirectory 'Balkan_Collapse.mod'
if (Test-Path -LiteralPath $targetMod) {
    Copy-Item -LiteralPath $targetMod -Destination (Join-Path $backupDirectory "Balkan_Collapse-$stamp") -Recurse -Force
    Remove-Item -LiteralPath $targetMod -Recurse -Force
}
if (Test-Path -LiteralPath $targetDescriptor) {
    Copy-Item -LiteralPath $targetDescriptor -Destination (Join-Path $backupDirectory "Balkan_Collapse-$stamp.mod") -Force
}
Copy-Item -LiteralPath $sourceMod -Destination $targetMod -Recurse -Force
Copy-Item -LiteralPath $sourceDescriptor -Destination $targetDescriptor -Force

$loadFile = Join-Path $hoiData 'dlc_load.json'
if (Test-Path -LiteralPath $loadFile) {
    Copy-Item -LiteralPath $loadFile -Destination (Join-Path $backupDirectory "dlc_load-$stamp.json") -Force
    try {
        $settings = Get-Content -LiteralPath $loadFile -Raw | ConvertFrom-Json -ErrorAction Stop
    } catch {
        Stop-WithMessage "не удалось прочитать dlc_load.json. Резервная копия сохранена в $backupDirectory; файл не перезаписан."
    }
} else {
    $settings = [pscustomobject]@{ disabled_dlcs = @(); enabled_mods = @() }
}
if ($null -eq $settings) {
    $settings = [pscustomobject]@{ disabled_dlcs = @(); enabled_mods = @() }
}
if ($settings.PSObject.Properties.Name -notcontains 'disabled_dlcs') {
    $settings | Add-Member -MemberType NoteProperty -Name disabled_dlcs -Value @()
}
if ($settings.PSObject.Properties.Name -notcontains 'enabled_mods') {
    $settings | Add-Member -MemberType NoteProperty -Name enabled_mods -Value @()
}
$settings.enabled_mods = @('mod/Balkan_Collapse.mod')
$json = $settings | ConvertTo-Json -Depth 20
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($loadFile, $json, $utf8NoBom)

Write-Host "`nМод установлен и включён в dlc_load.json." -ForegroundColor Green
Write-Host "Резервные копии: $backupDirectory"

# Find the Steam library and start HOI4 directly, so the Launcher cannot switch back to a different playset.
$steamRoots = @()
try {
    $steamUser = Get-ItemProperty -Path 'HKCU:\Software\Valve\Steam' -ErrorAction Stop
    if ($steamUser.SteamPath) { $steamRoots += $steamUser.SteamPath }
    if ($steamUser.InstallPath) { $steamRoots += $steamUser.InstallPath }
} catch { }
try {
    $steamMachine = Get-ItemProperty -Path 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam' -ErrorAction Stop
    if ($steamMachine.InstallPath) { $steamRoots += $steamMachine.InstallPath }
} catch { }
if ($env:ProgramFiles) { $steamRoots += (Join-Path $env:ProgramFiles 'Steam') }
if (${env:ProgramFiles(x86)}) { $steamRoots += (Join-Path ${env:ProgramFiles(x86)} 'Steam') }
$steamRoots = @($steamRoots | Where-Object { $_ } | Select-Object -Unique)

$libraryRoots = @($steamRoots)
foreach ($root in $steamRoots) {
    $vdf = Join-Path $root 'steamapps\libraryfolders.vdf'
    if (Test-Path -LiteralPath $vdf) {
        $contents = Get-Content -LiteralPath $vdf -Raw
        foreach ($match in [regex]::Matches($contents, '"path"\s+"([^"]+)"')) {
            $library = $match.Groups[1].Value.Replace('\\', '\')
            if ($library) { $libraryRoots += $library }
        }
    }
}
$gameExe = $null
foreach ($library in ($libraryRoots | Select-Object -Unique)) {
    $candidate = Join-Path $library 'steamapps\common\Hearts of Iron IV\hoi4.exe'
    if (Test-Path -LiteralPath $candidate) { $gameExe = $candidate; break }
}
if ($gameExe) {
    Write-Host 'Запускаю Hearts of Iron IV с включённым Balkan Collapse...' -ForegroundColor Cyan
    Start-Process -FilePath $gameExe -WorkingDirectory (Split-Path -Parent $gameExe)
} else {
    Write-Host 'Не нашёл hoi4.exe в библиотеках Steam. Открываю страницу запуска игры через Steam.' -ForegroundColor Yellow
    try {
        Start-Process 'steam://rungameid/394360'
    } catch {
        Stop-WithMessage 'не удалось запустить игру автоматически. Мод установлен и включён; запусти HOI4 через Steam.'
    }
}
