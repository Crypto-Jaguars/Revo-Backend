@echo off
setlocal enabledelayedexpansion

REM Database backup script for Revo-Backend
REM Usage: backup.bat [label]

REM Load environment variables from .env file
if exist .env (
  for /F "tokens=*" %%a in ('type .env ^| findstr /v "^#"') do (
    set %%a
  )
)

REM Default values
if not defined POSTGRES_HOST set POSTGRES_HOST=localhost
if not defined POSTGRES_PORT set POSTGRES_PORT=5432
if not defined POSTGRES_USER set POSTGRES_USER=myuser
if not defined POSTGRES_DB set POSTGRES_DB=mydatabase
if not defined BACKUP_DIR set BACKUP_DIR=.\backups
if not defined BACKUP_COMPRESSION_LEVEL set COMPRESSION=9
if not defined BACKUP_PREFIX set PREFIX=revo-db-backup

REM Create label from argument or default to empty
set LABEL=
if not "%~1"=="" (
  set LABEL=-%~1
)

REM Create backup directory if it doesn't exist
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Generate timestamp and filename
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "TIMESTAMP=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%-%dt:~8,2%-%dt:~10,2%-%dt:~12,2%"
set "FILENAME=%PREFIX%-manual%LABEL%-%TIMESTAMP%.sql.gz"
set "BACKUP_PATH=%BACKUP_DIR%\%FILENAME%"

echo Starting database backup to %BACKUP_PATH%

REM Check if password is defined
if not defined POSTGRES_PASSWORD (
  echo Error: POSTGRES_PASSWORD environment variable is not set
  exit /b 1
)

REM Perform the backup
set PGPASSWORD=%POSTGRES_PASSWORD%
pg_dump -h %POSTGRES_HOST% -p %POSTGRES_PORT% -U %POSTGRES_USER% -d %POSTGRES_DB% | gzip -%COMPRESSION% > "%BACKUP_PATH%"

REM Check if backup was successful
if %ERRORLEVEL% equ 0 (
  REM Validate the backup
  gzip -t "%BACKUP_PATH%"
  if %ERRORLEVEL% equ 0 (
    echo Backup completed successfully: %BACKUP_PATH%
    for /f "tokens=1" %%a in ('dir /a /-c "%BACKUP_PATH%" ^| findstr /r /c:"[0-9]* File"') do set "size=%%a"
    echo Backup size: !size! bytes
    exit /b 0
  ) else (
    echo Backup validation failed!
    del "%BACKUP_PATH%"
    exit /b 1
  )
) else (
  echo Backup failed!
  if exist "%BACKUP_PATH%" del "%BACKUP_PATH%"
  exit /b 1
)