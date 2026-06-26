#!/bin/bash
# Database Reset Script for Odoo

echo "======================================"
echo "Odoo Database Sequence Fix"
echo "======================================"

# Connect to PostgreSQL and drop the problematic sequence
psql -U odoo -d data -c "DROP SEQUENCE IF EXISTS base_registry_signaling CASCADE;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Dropped problematic sequence"
else
    echo "ℹ Sequence may not exist - continuing"
fi

# Now try to start Odoo with the fixed modules
echo ""
echo "Starting Odoo with updated modules..."
python3 odoo-bin.py -c odoo.conf -u all --limit-time-cpu=0 --limit-time-real=0 &
ODOO_PID=$!

# Wait a bit for initialization
sleep 10

# Check if Odoo is still running
if kill -0 $ODOO_PID 2>/dev/null; then
    echo "✓ Odoo started successfully!"
    echo "Server running (PID: $ODOO_PID)"
    echo ""
    echo "Access at: http://localhost:8069"
else
    echo "✗ Odoo failed to start"
fi
