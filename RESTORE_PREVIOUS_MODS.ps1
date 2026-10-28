$ErrorActionPreference = 'Stop'
$documents = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::MyDocuments)
$hoiData = Join-Path $documents 'Paradox Interactive\Hearts of Iron IV'
$backupDirectory = Join-Path $hoiData 'Balkan_Collapse_backups'
if (!(Test-Path -LiteralPath $backupDirectory)) {
    Write-Host 'Не найдена папка резервных копий.' -ForegroundColor Red
    exit 1
}
$backup = Get-ChildItem -LiteralPath $backupDirectory -Filter 'dlc_load-*.json' -File |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (!$backup) {
    Write-Host 'Нет резервной копии dlc_load.json.' -ForegroundColor Red
    exit 1
}
$loadFile = Join-Path $hoiData 'dlc_load.json'
Copy-Item -LiteralPath $backup.FullName -Destination $loadFile -Force
Write-Host "Восстановлен список модов из $($backup.Name)" -ForegroundColor Green
