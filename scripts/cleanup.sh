#!/bin/bash
# scripts/cleanup.sh - Cleanup old data

echo "🧹 Starting cleanup..."

# Clean old logs (keep last 7 days)
find logs -name "*.log" -type f -mtime +7 -delete

# Clean old backups (keep last 30 days)
find backups -name "*.tar.gz" -type f -mtime +30 -delete

# Clean Redis old keys
redis-cli KEYS "temp:*" | xargs redis-cli DEL

# Clean database old records
python -c "
from datetime import datetime, timedelta
from src.database.connection import db
db.opportunities.delete_many({'timestamp': {'$lt': datetime.now() - timedelta(days=30)}})
"

echo "✅ Cleanup complete"