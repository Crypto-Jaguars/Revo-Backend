# Database Backup and Recovery System

This module provides automated backup and recovery capabilities for the Revo-Backend application's PostgreSQL database.

## Features

- Scheduled automatic backups
- Manual backup creation
- Backup validation
- Backup retention management
- Database restoration
- Backup monitoring and status reporting

## Configuration

Backup settings can be configured through environment variables:

| Environment Variable        | Description                          | Default                   |
| --------------------------- | ------------------------------------ | ------------------------- |
| BACKUP_DIR                  | Directory where backups are stored   | ./backups                 |
| BACKUP_RETENTION_DAYS       | Number of days to keep backups       | 30                        |
| BACKUP_SCHEDULE             | Cron schedule for automatic backups  | 0 2 \* \* \* (2 AM daily) |
| BACKUP_COMPRESSION_LEVEL    | Gzip compression level (1-9)         | 9                         |
| BACKUP_ENABLE_NOTIFICATIONS | Enable email notifications           | false                     |
| BACKUP_NOTIFICATION_EMAIL   | Email address for notifications      |                           |
| BACKUP_MAX_CONCURRENT       | Maximum concurrent backup operations | 1                         |
| BACKUP_VALIDATE             | Validate backups after creation      | true                      |
| BACKUP_PREFIX               | Prefix for backup filenames          | revo-db-backup            |

## Usage

### Programmatic Usage

```typescript
// Inject the backup service
constructor(private readonly backupService: BackupService) {}

// Create a manual backup
async createManualBackup() {
  const backupPath = await this.backupService.createBackup({
    manual: true,
    label: 'pre-deployment'
  });
  console.log(`Backup created at: ${backupPath}`);
}

// Restore from a backup
async restoreFromBackup(backupPath: string) {
  await this.backupService.restoreBackup(backupPath);
}

// List available backups
async listBackups() {
  const backups = await this.backupService.listBackups();
  console.log(backups);
}

// Get backup system status
async getStatus() {
  const status = await this.backupService.getBackupStatus();
  console.log(status);
}
```
