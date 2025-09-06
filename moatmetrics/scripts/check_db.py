import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data/moatmetrics.db')

# Get list of tables
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
print("Tables in database:")
print(tables)

# Check invoice count
invoice_count = pd.read_sql_query("SELECT COUNT(*) as count FROM invoices;", conn)
print(f"\nInvoices in database: {invoice_count['count'][0]}")

# Check first few invoices
if invoice_count['count'][0] > 0:
    invoices = pd.read_sql_query("SELECT * FROM invoices LIMIT 3;", conn)
    print("\nSample invoices:")
    print(invoices[['invoice_id', 'client_id', 'invoice_number', 'total_amount']])

conn.close()
