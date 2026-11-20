
# Kopano Inventory Database Recovery
# BFB321 Group 15

$ErrorActionPreference = "Stop"

$BackupFolder = Join-Path $PSScriptRoot "..\backups"
$BackupFolder = [System.IO.Path]::GetFullPath($BackupFolder)

Write-Host "Kopano Database Recovery"
Write-Host "Available backups:"
Get-ChildItem -Path $BackupFolder -Filter "*.sql" |
    Select-Object Name, Length, LastWriteTime |
    Format-Table -AutoSize

$BackupName = Read-Host "Enter the exact backup filename"

$BackupFile = Join-Path $BackupFolder $BackupName

if (-not (Test-Path $BackupFile -PathType Leaf)) {
    throw "Backup file not found."
}

Write-Warning "Restoring a backup can overwrite existing database data."
$Confirmation = Read-Host "Type RESTORE to continue"

if ($Confirmation -cne "RESTORE") {
    Write-Host "Recovery cancelled."
    exit
}

Write-Host "Starting database recovery..."

$Command = 'mysql --user=root --password < "' + $BackupFile + '"'
& cmd.exe /c $Command

if ($LASTEXITCODE -ne 0) {
    throw "Database recovery failed."
}

Write-Host "Database recovery completed."
