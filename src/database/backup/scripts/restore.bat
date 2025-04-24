@echo off
setlocal enabledelayedexpansion

REM Database restore script for Revo-Backend
REM Usage: restore.bat <backup_file>

REM Load environment variables
if exist .env (
  for /f "tokens=*" %%a in (.env) do (
    set %%a
  )
)

REM Default values
if not defined POSTGRES_HOST set POSTGRES_HOST=localhost
if not defined POSTGRES_PORT set POSTGRES_PORT=5432
if not defined POSTGRES_USER set POSTGRES_USER=myuser
if not defined POSTGRES_DB set POSTGRES_DB=mydatabase

REM Check if backup file is provided
if "%~1"=="" (
  echo Error: No backup file specified
  echo Usage: restore.bat ^<backup_file^>
  exit /b 1
)

set "BACKUP_FILE=%~1"

REM Check if backup file exists
if not exist "%BACKUP_FILE%" (
  echo Error: Backup file does not exist: %BACKUP_FILE%
  exit /b 1
)

REM Validate the backup file
echo Validating backup file...
gzip -t "%BACKUP_FILE%"
if %ERRORLEVEL% neq 0 (
  echo Error: Backup file is corrupted: %BACKUP_FILE%
  exit /b 1
)

echo WARNING: This will overwrite the current database (%POSTGRES_DB%)!
set /p CONFIRM=Are you sure you want to continue? (y/n): 

if /i not "%CONFIRM%"=="y" (
  echo Restore cancelled.
  exit /b 0
)

echo Starting database restoration from %BACKUP_FILE%

REM Perform the restoration
if not defined POSTGRES_PASSWORD (
  echo Error: POSTGRES_PASSWORD environment variable is not set
  exit /b 1
)
set PGPASSWORD=%POSTGRES_PASSWORD%
gzip -cd "%BACKUP_FILE%" | psql -h %POSTGRES_HOST% -p %POSTGRES_PORT% -U %POSTGRES_USER% -d %POSTGRES_DB%

REM Check if restoration was successful
if %ERRORLEVEL% equ 0 (
  echo Database restoration completed successfully from %BACKUP_FILE%
  exit /b 0
) else (
  echo Database restoration failed!
  exit /b 1
)