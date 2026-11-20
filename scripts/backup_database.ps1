
# Kopano Inventory Database Backup
# BFB321 Group 15

$ErrorActionPreference = "Stop"

$BackupFolder = Join-Path $PSScriptRoot "..\backups"
$BackupFolder = [System.IO.Path]::GetFullPath($BackupFolder)

if (-not (Test-Path $BackupFolder)) {
    New-Item -ItemType Directory -Path $BackupFolder | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = Join-Path $BackupFolder "kopano_inventory_$Timestamp.sql"

$Database = "kopano_inventory"
$MySQLDump = "mysqldump"

Write-Host "Starting Kopano database backup..."

& $MySQLDump --user=root --password --databases $Database --result-file="$BackupFile"

if ($LASTEXITCODE -ne 0) {
    throw "Database backup failed."
}

Write-Host "Backup completed successfully:"
Write-Host $BackupFile
