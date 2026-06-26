#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "=== Drop all base_*_signaling sequences (safe mode) ==="

# Find all databases that allow connections
DBS=$(sudo -u postgres psql -At -c "SELECT datname FROM pg_database WHERE datallowconn")

if [ -z "$DBS" ]; then
  echo "No databases found. Exiting."
  exit 0
fi

for db in $DBS; do
  echo "\n---- Checking DB: $db ----"
  SEQS=$(sudo -u postgres psql -d "$db" -At -c "SELECT nspname||'.'||relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE relkind='S' AND relname LIKE 'base_%_signaling';")
  if [ -z "$SEQS" ]; then
    echo "No signaling sequences in $db"
    continue
  fi

  echo "Signaling sequences found in $db:"
  echo "$SEQS"

  # Backup DB before dropping sequences
  BACKUP=/tmp/${db}.dump
  echo "Creating dump $BACKUP ..."
  sudo -u postgres pg_dump -Fc -f "$BACKUP" "$db"
  echo "Dump created: $BACKUP"

  # Drop each sequence found
  echo "$SEQS" | while IFS= read -r seq; do
    # seq is schema.sequence
    echo "Dropping sequence $seq in $db"
    sudo -u postgres psql -d "$db" -c "DROP SEQUENCE IF EXISTS \"${seq##*.}\" CASCADE;"
  done
  echo "Done clearing signaling sequences for $db"
done

# Restart PostgreSQL to be safe
echo "\nRestarting PostgreSQL..."
sudo systemctl restart postgresql
sleep 2
sudo systemctl status postgresql --no-pager | sed -n '1,5p'

# Restart Odoo
echo "\nRestarting Odoo (if running) and starting a fresh instance..."
pkill -f "python3 odoo-bin" 2>/dev/null || true
sleep 1
nohup python3 odoo-bin.py -c odoo.conf > /tmp/odoo.log 2>&1 &
ODOO_PID=$!
sleep 6

echo "Odoo started with PID: $ODOO_PID"

echo "==== Tail /tmp/odoo.log (last 120 lines) ===="
tail -n 120 /tmp/odoo.log || true

echo "Script finished. If you still see duplicate-sequence errors, paste the above log lines here for further analysis."
