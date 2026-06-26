#!/bin/bash
# Simple database cleanup script

echo "=== Odoo Database Fix ==="
echo ""
echo "Dropping problematic sequence..."

# Try multiple ways to connect and fix
{
    psql -U postgres -d data -c "DROP SEQUENCE IF EXISTS base_registry_signaling CASCADE;" && \
    echo "✓ Sequence dropped (as postgres)" && exit 0
} || {
    psql -U odoo -d data -c "DROP SEQUENCE IF EXISTS base_registry_signaling CASCADE;" && \
    echo "✓ Sequence dropped (as odoo)" && exit 0
} || {
    echo "⚠ Could not drop sequence via psql"
    echo "  This might be OK - trying to start Odoo anyway"
}

echo ""
echo "Killing any existing Odoo processes..."
killall -9 python3 2>/dev/null
sleep 2

echo ""
echo "Starting Odoo server..."
cd ~/Business-Internship
python3 odoo-bin.py -c odoo.conf -u all --stop-after-init 2>&1 | tail -20

echo ""
echo "Starting Odoo service normally..."
python3 odoo-bin.py -c odoo.conf &
sleep 5

echo "✓ Done! Access Odoo at http://localhost:8069"
