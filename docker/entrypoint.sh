#!/usr/bin/env bash
# opt migration and production server start

set -e

if [ -n "$1" ] & [ "$1" == "migrate" ]
then
    echo "Migrating database in 5s..."
    sleep 5
    echo "... migrating database now"
    alembic upgrade head
fi

python alembic/test_alembic.py
gunicorn \
  -k "uvicorn.workers.UvicornWorker" \
  -c "app/gunicorn_conf.py" \
  "app.app:app"

set +e