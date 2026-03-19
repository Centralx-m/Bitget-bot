#!/bin/bash
# scripts/backup.sh - Backup script

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "📦 Creating backup at $BACKUP_DIR/backup_$TIMESTAMP"

# Create backup directory
mkdir -p $BACKUP_DIR/backup_$TIMESTAMP

# Backup logs
cp -r logs $BACKUP_DIR/backup_$TIMESTAMP/

# Backup .env (without secrets)
cp .env.example $BACKUP_DIR/backup_$TIMESTAMP/

# Backup database if exists
if [ -f "data/trades.db" ]; then
    cp data/trades.db $BACKUP_DIR/backup_$TIMESTAMP/
fi

# Compress backup
tar -czf $BACKUP_DIR/backup_$TIMESTAMP.tar.gz -C $BACKUP_DIR backup_$TIMESTAMP
rm -rf $BACKUP_DIR/backup_$TIMESTAMP

echo "✅ Backup created: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"