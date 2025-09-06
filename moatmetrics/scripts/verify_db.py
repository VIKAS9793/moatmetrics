#!/usr/bin/env python3
"""
Verify database table counts after data upload
"""
import sqlite3

def verify_database():
    print("\n📊 Database Verification")
    print("========================")
    
    conn = sqlite3.connect('data/moatmetrics.db')
    
    tables = [
        ('clients', '👥'),
        ('invoices', '📄'),
        ('time_logs', '⏰'),
        ('licenses', '🔑')
    ]
    
    for table, icon in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"   {icon} {table}: {count} records")
    
    conn.close()

if __name__ == "__main__":
    verify_database()
