#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Sequence Fix Utility for Odoo
Fixes the 'base_registry_signaling' sequence already exists error
"""

import os
import sys
import subprocess
import psycopg2
from configparser import ConfigParser

def read_odoo_config(config_file):
    """Read Odoo configuration file"""
    config = ConfigParser()
    config.read(config_file)
    
    db_config = {
        'host': config.get('options', 'db_host', fallback='localhost'),
        'port': int(config.get('options', 'db_port', fallback='5432')),
        'user': config.get('options', 'db_user', fallback='odoo'),
        'password': config.get('options', 'db_password', fallback=''),
        'database': config.get('options', 'db_name', fallback='data'),
    }
    return db_config

def fix_database(db_config):
    """Drop the problematic sequence"""
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = conn.cursor()
        
        print("[*] Connecting to database:", db_config['database'])
        
        # Drop the problematic sequence
        print("[*] Dropping base_registry_signaling sequence...")
        cursor.execute("DROP SEQUENCE IF EXISTS base_registry_signaling CASCADE;")
        conn.commit()
        
        print("✓ Successfully dropped problematic sequence")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"⚠ Error accessing database: {e}")
        print("  Make sure PostgreSQL is running and credentials are correct")
        return False

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 50)
    print("Odoo Database Sequence Fix Utility")
    print("=" * 50)
    
    # Read configuration
    if not os.path.exists('odoo.conf'):
        print("✗ odoo.conf not found in current directory")
        sys.exit(1)
    
    db_config = read_odoo_config('odoo.conf')
    
    # Fix database
    if fix_database(db_config):
        print("\n[*] Database fixed! Now starting Odoo...")
        print("[*] Command: python3 odoo-bin.py -c odoo.conf -u all")
        print("\nYou can now run: python3 odoo-bin.py -c odoo.conf -u all")
    else:
        print("\n✗ Failed to fix database. Please check PostgreSQL connection.")
        sys.exit(1)

if __name__ == '__main__':
    main()
