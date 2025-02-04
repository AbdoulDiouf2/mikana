#!/bin/sh

# Attendre que MySQL soit prêt
echo "Waiting for MySQL to be ready..."
while ! nc -z mysql 3306; do
  sleep 1
done
echo "MySQL is ready!"

# Exécuter le script de migration
python migrate_to_mysql.py

# Démarrer l'application
exec uvicorn src.api.prediction_service:app --host 0.0.0.0 --port 8000 --reload
