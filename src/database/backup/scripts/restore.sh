#!/bin/bash

# Database restore script for Revo-Backend
# Usage: ./restore.sh <backup_file_path>

# Check if backup file is provided
if [ -z "$1" ]; then
  echo "Error: No backup file specified"
  echo "Usage: ./restore.sh <backup_file_path>"
  exit 1
fi

BACKUP_FILE="$1"

# Check if the backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
  echo "Error: Backup file does not exist: $BACKUP_FILE"
  exit 1
fi

# Load environment variables
if [ -f .env ]; then
  export "$(grep -v '^#' .env | xargs)"
fi

# Default values
DB_HOST=${POSTGRES_HOST:-localhost}
DB_PORT=${POSTGRES_PORT:-5432}
DB_USER=${POSTGRES_USER:-myuser}
DB_NAME=${POSTGRES_DB:-mydatabase}

# Check if password is defined
if [ -z "$POSTGRES_PASSWORD" ]; then
  echo "Error: POSTGRES_PASSWORD environment variable is not set"
  exit 1
fi

echo "Starting database restoration from $BACKUP_FILE"
echo "WARNING: This will overwrite the current database. Press Ctrl+C to cancel."
echo "Continuing in 5 seconds..."
sleep 5

# Perform the restoration
echo "Restoring database from backup..."
PGPASSWORD=$POSTGRES_PASSWORD gunzip -c "$BACKUP_FILE" | psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME

# Check if restoration was successful
if [ $? -eq 0 ]; then
  echo "Database restoration completed successfully from $BACKUP_FILE"
  exit 0
else
  echo "Database restoration failed!"
  exit 1
fi