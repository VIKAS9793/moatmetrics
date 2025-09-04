#!/usr/bin/env python
"""Manually load all data into the database."""

import sys
sys.path.append('.')

from pathlib import Path
import pandas as pd
from src.etl.csv_processor import CSVProcessor
from src.utils.database import get_db_manager

def load_all_data():
    """Load all CSV data into the database."""
    
    # Setup
    db_manager = get_db_manager()
    db_session = db_manager.get_session()
    processor = CSVProcessor(db_session)
    
    data_files = [
        ("clients", "moatmetrics/data/raw/clients.csv"),
        ("invoices", "moatmetrics/data/raw/invoices.csv"),
        ("time_logs", "moatmetrics/data/raw/time_logs.csv"),
        ("licenses", "moatmetrics/data/raw/licenses.csv")
    ]
    
    for data_type, file_path in data_files:
        csv_path = Path(file_path)
        if not csv_path.exists():
            print(f"File not found: {file_path}")
            continue
            
        print(f"\nProcessing {data_type}...")
        df = pd.read_csv(csv_path)
        print(f"  Rows in CSV: {len(df)}")
        
        # Process based on type
        if data_type == "clients":
            records_processed, records_failed = processor._process_clients(df, False, False)
        elif data_type == "invoices":
            records_processed, records_failed = processor._process_invoices(df, False, False)
        elif data_type == "time_logs":
            records_processed, records_failed = processor._process_time_logs(df, False, False)
        elif data_type == "licenses":
            records_processed, records_failed = processor._process_licenses(df, False, False)
        
        print(f"  Processed: {records_processed}, Failed: {records_failed}")
        
        if processor.validation_errors:
            print(f"  Errors: {len(processor.validation_errors)}")
            for err in processor.validation_errors[:3]:  # Show first 3 errors
                print(f"    - Row {err['row']}: {err['error']}")
    
    # Commit all changes
    db_session.commit()
    print("\n✓ All data committed to database")
    
    # Verify
    from src.utils.database import Client, Invoice, TimeLog, License
    print("\nDatabase Summary:")
    print(f"  Clients: {db_session.query(Client).count()}")
    print(f"  Invoices: {db_session.query(Invoice).count()}")
    print(f"  Time Logs: {db_session.query(TimeLog).count()}")
    print(f"  Licenses: {db_session.query(License).count()}")
    
    db_session.close()

if __name__ == "__main__":
    load_all_data()
