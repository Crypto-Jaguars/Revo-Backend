#!/bin/bash

# Database backup script for Revo-Backend
# Usage: ./backup.sh [label]

# Load environment variables
set -a
[ -f .env ] && . .env
set +a

# Default values
DB_HOST=${POSTGRES_HOST:-localhost}
DB_PORT=${POSTGRES_PORT:-5432}
DB_USER=${POSTGRES_USER:-myuser}
DB_NAME=${POSTGRES_DB:-mydatabase}
BACKUP_DIR=${BACKUP_DIR:-./backups}
COMPRESSION=${BACKUP_COMPRESSION_LEVEL:-9}
PREFIX=${BACKUP_PREFIX:-revo-db-backup}

# Check if password is defined
if [ -z "$POSTGRES_PASSWORD" ]; then
  echo "Error: POSTGRES_PASSWORD environment variable is not set"
  exit 1
fi

# Create label from argument or default to empty
LABEL=""
if [ ! -z "$1" ]; then
  LABEL="-$1"
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate timestamp and filename
TIMESTAMP=$(date +"%Y-%m-%d-%H-%M-%S")
FILENAME="${PREFIX}-manual${LABEL}-${TIMESTAMP}.sql.gz"
BACKUP_PATH="${BACKUP_DIR}/${FILENAME}"

echo "Starting database backup to ${BACKUP_PATH}"

# Perform the backup
PGPASSWORD=$POSTGRES_PASSWORD pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME | gzip -$COMPRESSION > "$BACKUP_PATH"

# Check if backup was successful
if [ $? -eq 0 ]; then
  # Validate the backup
  gzip -t "$BACKUP_PATH"
  if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_PATH"
    echo "Backup size: $(du -h "$BACKUP_PATH" | cut -f1)"
    exit 0
  else
    echo "Backup validation failed!"
    rm "$BACKUP_PATH"
    exit 1
  fi
else
  echo "Backup failed!"
  if [ -f "$BACKUP_PATH" ]; then
    rm "$BACKUP_PATH"
  fi
  exit 1
fi