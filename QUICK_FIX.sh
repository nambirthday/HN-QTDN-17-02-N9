#!/bin/bash
# COMPLETE ODOO TROUBLESHOOTING & RESTART SCRIPT
# Run this directly in WSL terminal

echo "=============================================="
echo "ODOO DATABASE & PERMISSION FIX"
echo "=============================================="
echo ""

# Step 1: Kill any running Odoo processes
echo "[1/5] Stopping Odoo..."
pkill -f "python3 odoo-bin" 2>/dev/null || true
sleep 2
echo "✓ Done"
echo ""

# Step 2: Fix database sequence issue
echo "[2/5] Fixing database sequence..."
psql -U postgres -d data -c "DROP SEQUENCE IF EXISTS base_registry_signaling CASCADE;" 2>&1 | grep -i "error\|drop" || echo "✓ Sequence fixed"
echo ""

# Step 3: Fix PostgreSQL permissions (run as postgres user)
echo "[3/5] Checking PostgreSQL permissions..."
sudo -u postgres psql -d data -c "GRANT ALL PRIVILEGES ON DATABASE data TO odoo;" 2>&1 | grep -v "already\|Error" || true
sudo -u postgres psql -d data -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO odoo;" 2>&1 | grep -v "already\|Error" || true
sudo -u postgres psql -d data -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO odoo;" 2>&1 | grep -v "already\|Error" || true
echo "✓ Permissions updated"
echo ""

# Step 4: Start Odoo with initialization
echo "[4/5] Starting Odoo server..."
cd ~/Business-Internship
nohup python3 odoo-bin.py -c odoo.conf > /tmp/odoo.log 2>&1 &
ODOO_PID=$!
echo "✓ Odoo started (PID: $ODOO_PID)"
echo ""

# Step 5: Wait and verify
echo "[5/5] Waiting for Odoo to initialize..."
sleep 10

# Check if Odoo is running
if ps -p $ODOO_PID > /dev/null; then
    echo "✓ SUCCESS! Odoo is running"
    echo ""
    echo "Access Odoo at: http://localhost:8069"
    echo "Log file: /tmp/odoo.log"
    echo ""
    echo "Tail log in another terminal with:"
    echo "  tail -f /tmp/odoo.log"
else
    echo "✗ Odoo failed to start"
    echo "Last 30 lines of log:"
    tail -30 /tmp/odoo.log
    exit 1
fi
