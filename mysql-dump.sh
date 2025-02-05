#!/bin/bash
if [ -f "/dumps/backup.sql" ]; then
    mysql -u root -padmin mikana_db < /dumps/backup.sql
fi

trap 'mysqldump -u root -padmin mikana_db metrics_history > /dumps/backup.sql' SIGTERM

exec docker-entrypoint.sh mysqld