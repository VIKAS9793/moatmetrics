"""
CSV processor for ETL operations in MoatMetrics.

This module handles CSV file ingestion, validation, and normalization
with comprehensive error handling and data quality assessment.
"""

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import uuid

import pandas as pd
import duckdb
from pydantic import ValidationError
from sqlalchemy.orm import Session
from loguru import logger

from ..utils.database import (
    get_db_manager, Client, Invoice, TimeLog, License, 
    DataSnapshot, AuditLog, ActionType
)
from ..utils.schemas import (
    ClientCreate, InvoiceCreate, TimeLogCreate, LicenseCreate,
    InvoiceLineItem, DataQualityFlag, FileUploadResponse
)
from ..utils.config_loader import get_config


class CSVProcessor:
    """
    Handles CSV file processing, validation, and database ingestion.
    
    This class provides comprehensive CSV processing capabilities including
    validation, normalization, quality assessment, and database storage.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize CSV processor.
        
        Args:
            db_session: Optional database session
        """
        self.config = get_config()
        self.db_manager = get_db_manager()
        self.db_session = db_session or self.db_manager.get_session()
        self.logger = logger.bind(module="csv_processor")
        self.validation_errors: List[Dict[str, Any]] = []
        self.data_quality_flags: List[DataQualityFlag] = []
        
    def process_file(
        self, 
        file_path: Path,
        data_type: str,
        validate_schema: bool = True,
        create_snapshot: bool = True,
        dry_run: bool = False,
        actor: str = "system"
    ) -> FileUploadResponse:
        """
        Process a CSV file through the ETL pipeline.
        
        Args:
            file_path: Path to CSV file
            data_type: Type of data (clients, invoices, time_logs, licenses)
            validate_schema: Whether to perform schema validation
            create_snapshot: Whether to create a data snapshot
            dry_run: If True, validate only without persisting
            actor: User or system performing the action
            
        Returns:
            FileUploadResponse with processing results
        """
        self.logger.info(f"Processing {data_type} file: {file_path}")
        
        try:
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config.etl.max_file_size_mb:
                raise ValueError(f"File size {file_size_mb:.2f}MB exceeds limit of {self.config.etl.max_file_size_mb}MB")
            
            # Create snapshot if requested
            snapshot_id = None
            if create_snapshot and not dry_run:
                snapshot_id = self._create_snapshot(file_path, data_type, actor)
            
            # Read and validate CSV
            df = self._read_csv(file_path)
            self._assess_data_quality(df, data_type)
            
            # Process based on data type
            records_processed = 0
            records_failed = 0
            
            if data_type == "clients":
                records_processed, records_failed = self._process_clients(df, validate_schema, dry_run)
            elif data_type == "invoices":
                records_processed, records_failed = self._process_invoices(df, validate_schema, dry_run)
            elif data_type == "time_logs":
                records_processed, records_failed = self._process_time_logs(df, validate_schema, dry_run)
            elif data_type == "licenses":
                records_processed, records_failed = self._process_licenses(df, validate_schema, dry_run)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                records_processed, records_failed, len(self.validation_errors)
            )
            
            # Log audit entry
            if not dry_run:
                self._log_audit(
                    actor=actor,
                    action=ActionType.DATA_UPLOAD,
                    target=str(file_path),
                    success=records_failed == 0,
                    details={
                        "data_type": data_type,
                        "records_processed": records_processed,
                        "records_failed": records_failed,
                        "snapshot_id": snapshot_id
                    }
                )
            
            # Session management handled by API dependency injection
            if not dry_run:
                self.logger.info(f"Successfully processed {records_processed} records")
            else:
                self.db_session.rollback()
                self.logger.info(f"Dry run completed: {records_processed} records validated")
            
            return FileUploadResponse(
                success=records_failed == 0,
                records_processed=records_processed,
                records_failed=records_failed,
                validation_errors=self.validation_errors[:100],  # Limit errors returned
                snapshot_id=snapshot_id,
                data_quality_flags=list(set(self.data_quality_flags)),
                confidence_score=confidence_score
            )
            
        except Exception as e:
            self.logger.error(f"Error processing file: {e}")
            self.db_session.rollback()
            
            # Log failed audit entry
            self._log_audit(
                actor=actor,
                action=ActionType.DATA_UPLOAD,
                target=str(file_path),
                success=False,
                error_message=str(e),
                details={"data_type": data_type}
            )
            
            return FileUploadResponse(
                success=False,
                records_processed=0,
                records_failed=0,
                validation_errors=[{"error": str(e)}],
                snapshot_id=None,
                data_quality_flags=[DataQualityFlag.INCONSISTENT],
                confidence_score=0.0
            )
    
    def _read_csv(self, file_path: Path) -> pd.DataFrame:
        """
        Read CSV file with encoding detection.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Pandas DataFrame
        """
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                self.logger.info(f"Successfully read CSV with {encoding} encoding")
                return df
            except UnicodeDecodeError:
                continue
        
        raise ValueError("Unable to detect file encoding")
    
    def _assess_data_quality(self, df: pd.DataFrame, data_type: str) -> None:
        """
        Assess data quality and set flags.
        
        Args:
            df: DataFrame to assess
            data_type: Type of data being processed
        """
        self.data_quality_flags = []
        
        # Check for missing values
        missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        if missing_ratio > 0.1:
            self.data_quality_flags.append(DataQualityFlag.MISSING_FIELDS)
        
        # Check for duplicates
        if df.duplicated().any():
            self.data_quality_flags.append(DataQualityFlag.DUPLICATE)
        
        # Check for outliers using IQR method for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).any()
            if outliers:
                self.data_quality_flags.append(DataQualityFlag.OUTLIER)
                break
        
        if not self.data_quality_flags:
            self.data_quality_flags.append(DataQualityFlag.COMPLETE)
    
    def _process_clients(
        self, 
        df: pd.DataFrame, 
        validate_schema: bool,
        dry_run: bool
    ) -> Tuple[int, int]:
        """
        Process client records.
        
        Args:
            df: DataFrame with client data
            validate_schema: Whether to validate against schema
            dry_run: If True, don't persist to database
            
        Returns:
            Tuple of (records_processed, records_failed)
        """
        records_processed = 0
        records_failed = 0
        
        for index, row in df.iterrows():
            try:
                # Convert row to dict and handle NaN values
                data = row.where(pd.notna(row), None).to_dict()
                
                # Validate with Pydantic if requested
                if validate_schema:
                    client_data = ClientCreate(
                        name=data.get('name'),
                        industry=data.get('industry'),
                        contact_email=data.get('email') or data.get('contact_email'),
                        contact_phone=data.get('phone') or data.get('contact_phone'),
                        is_active=data.get('is_active', True),
                        metadata={}
                    )
                    data = client_data.model_dump()
                
                if not dry_run:
                    # Check if client exists
                    existing = self.db_session.query(Client).filter_by(
                        name=data['name']
                    ).first()
                    
                    if existing:
                        # Update existing client
                        for key, value in data.items():
                            if hasattr(existing, key) and value is not None:
                                setattr(existing, key, value)
                        existing.updated_at = datetime.utcnow()
                    else:
                        # Create new client
                        client = Client(**data)
                        self.db_session.add(client)
                
                records_processed += 1
                
            except (ValidationError, KeyError, ValueError) as e:
                records_failed += 1
                self.validation_errors.append({
                    "row": index,
                    "error": str(e),
                    "data": row.to_dict()
                })
                self.logger.warning(f"Failed to process row {index}: {e}")
        
        return records_processed, records_failed
    
    def _process_invoices(
        self,
        df: pd.DataFrame,
        validate_schema: bool,
        dry_run: bool
    ) -> Tuple[int, int]:
        """
        Process invoice records.
        
        Args:
            df: DataFrame with invoice data
            validate_schema: Whether to validate against schema
            dry_run: If True, don't persist to database
            
        Returns:
            Tuple of (records_processed, records_failed)
        """
        records_processed = 0
        records_failed = 0
        
        for index, row in df.iterrows():
            try:
                # Create savepoint for this record to enable rollback on error
                if not dry_run:
                    self.db_session.begin_nested()
                
                data = row.where(pd.notna(row), None).to_dict()
                
                # Parse invoice lines from JSON or create default
                lines_data = []
                if 'lines_json' in data and data['lines_json']:
                    try:
                        lines_data = json.loads(data['lines_json'])
                    except json.JSONDecodeError:
                        lines_data = [{
                            "description": data.get('description', 'Service'),
                            "quantity": 1,
                            "unit_price": float(data.get('total_amount', 0)),
                            "tax_rate": 0,
                            "discount": 0
                        }]
                elif 'total_amount' in data:
                    lines_data = [{
                        "description": "Service",
                        "quantity": 1,
                        "unit_price": float(data['total_amount']),
                        "tax_rate": 0,
                        "discount": 0
                    }]
                
                # Get client ID - resolve from name if needed
                client_id = data.get('client_id')
                if not client_id and 'client_name' in data:
                    # Use no_autoflush to prevent premature flush during query
                    with self.db_session.no_autoflush:
                        client = self.db_session.query(Client).filter_by(
                            name=data['client_name']
                        ).first()
                        client_id = client.client_id if client else None
                
                if not client_id:
                    raise ValueError(f"Client not found for row {index}")
                
                # Process invoice data
                if validate_schema:
                    # Convert line items to Pydantic models for validation
                    lines = [InvoiceLineItem(**line) for line in lines_data]
                    
                    invoice_data = InvoiceCreate(
                        client_id=client_id,
                        invoice_number=data.get('invoice_number', f"INV-{index}"),
                        date=pd.to_datetime(data.get('date', datetime.now())),
                        due_date=pd.to_datetime(data.get('due_date')) if data.get('due_date') else None,
                        currency=data.get('currency', 'USD'),
                        status=data.get('status', 'pending'),
                        lines=lines
                    )
                    
                    # Extract validated data for database insertion
                    invoice_dict = {
                        'client_id': invoice_data.client_id,
                        'invoice_number': invoice_data.invoice_number,
                        'date': invoice_data.date,
                        'due_date': invoice_data.due_date,
                        'currency': invoice_data.currency,
                        'subtotal': invoice_data.subtotal,
                        'tax_amount': invoice_data.tax_amount,
                        'total_amount': invoice_data.total_amount,
                        'status': invoice_data.status,
                        'lines_json': [line.model_dump() for line in invoice_data.lines]
                    }
                else:
                    # Direct processing without schema validation
                    # Calculate totals from lines data
                    subtotal = sum(line.get('quantity', 1) * line.get('unit_price', 0) - line.get('discount', 0) 
                                  for line in lines_data)
                    tax_amount = sum((line.get('quantity', 1) * line.get('unit_price', 0) - line.get('discount', 0)) * line.get('tax_rate', 0) 
                                    for line in lines_data)
                    total_amount = data.get('total_amount', subtotal + tax_amount)
                    
                    invoice_dict = {
                        'client_id': client_id,
                        'invoice_number': data.get('invoice_number', f"INV-{index}"),
                        'date': pd.to_datetime(data.get('date', datetime.now())),
                        'due_date': pd.to_datetime(data.get('due_date')) if data.get('due_date') else None,
                        'currency': data.get('currency', 'USD'),
                        'subtotal': subtotal,
                        'tax_amount': tax_amount,
                        'total_amount': total_amount,
                        'status': data.get('status', 'pending'),
                        'lines_json': lines_data
                    }
                
                # Save to database if not a dry run
                if not dry_run:
                    # Check for duplicate invoice number first
                    existing = self.db_session.query(Invoice).filter_by(
                        invoice_number=invoice_dict['invoice_number']
                    ).first()
                    
                    if existing:
                        # Skip duplicate, don't fail entire batch
                        self.logger.info(f"Skipping duplicate invoice: {invoice_dict['invoice_number']}")
                        self.db_session.rollback()  # Rollback the savepoint
                        records_processed += 1  # Count as processed but skipped
                        continue
                    
                    invoice = Invoice(**invoice_dict)
                    self.db_session.add(invoice)
                    # Note: Savepoint will be committed with outer transaction
                
                records_processed += 1
                
            except Exception as e:
                records_failed += 1
                self.validation_errors.append({
                    "row": index,
                    "error": str(e),
                    "data": row.to_dict()
                })
                self.logger.warning(f"Failed to process row {index}: {e}")
                
                # Rollback only the current record's transaction
                if not dry_run:
                    try:
                        self.db_session.rollback()  # Rollback to savepoint
                    except:
                        # If rollback fails, create new session
                        self.db_session.close()
                        self.db_session = self.db_manager.get_session()
        
        return records_processed, records_failed
    
    def _process_time_logs(
        self,
        df: pd.DataFrame,
        validate_schema: bool,
        dry_run: bool
    ) -> Tuple[int, int]:
        """
        Process time log records.
        
        Args:
            df: DataFrame with time log data
            validate_schema: Whether to validate against schema
            dry_run: If True, don't persist to database
            
        Returns:
            Tuple of (records_processed, records_failed)
        """
        records_processed = 0
        records_failed = 0
        
        for index, row in df.iterrows():
            try:
                # Create savepoint for this record
                if not dry_run:
                    self.db_session.begin_nested()
                
                data = row.where(pd.notna(row), None).to_dict()
                
                # Get client ID
                client_id = data.get('client_id')
                if not client_id and 'client_name' in data:
                    # Use no_autoflush to prevent premature flush
                    with self.db_session.no_autoflush:
                        client = self.db_session.query(Client).filter_by(
                            name=data['client_name']
                        ).first()
                        client_id = client.client_id if client else None
                
                if not client_id:
                    raise ValueError(f"Client not found for row {index}")
                
                # Process time log data
                if validate_schema:
                    time_log_data = TimeLogCreate(
                        client_id=client_id,
                        staff_name=data.get('staff_name', 'Unknown'),
                        staff_email=data.get('staff_email'),
                        date=pd.to_datetime(data.get('date', datetime.now())),
                        hours=float(data.get('hours', 0)),
                        rate=float(data.get('rate', 0)),
                        project_name=data.get('project_name'),
                        task_description=data.get('task_description'),
                        billable=bool(data.get('billable', True))
                    )
                    
                    # Extract validated data
                    time_log_dict = {
                        'client_id': time_log_data.client_id,
                        'staff_name': time_log_data.staff_name,
                        'staff_email': time_log_data.staff_email,
                        'date': time_log_data.date,
                        'hours': time_log_data.hours,
                        'rate': time_log_data.rate,
                        'total_cost': time_log_data.total_cost,
                        'project_name': time_log_data.project_name,
                        'task_description': time_log_data.task_description,
                        'billable': time_log_data.billable
                    }
                else:
                    # Direct processing without validation
                    hours = float(data.get('hours', 0))
                    rate = float(data.get('rate', 0))
                    
                    time_log_dict = {
                        'client_id': client_id,
                        'staff_name': data.get('staff_name', 'Unknown'),
                        'staff_email': data.get('staff_email'),
                        'date': pd.to_datetime(data.get('date', datetime.now())),
                        'hours': hours,
                        'rate': rate,
                        'total_cost': hours * rate,
                        'project_name': data.get('project_name'),
                        'task_description': data.get('task_description'),
                        'billable': bool(data.get('billable', True))
                    }
                
                # Save to database if not a dry run
                if not dry_run:
                    time_log = TimeLog(**time_log_dict)
                    self.db_session.add(time_log)
                    # Note: Savepoint will be committed with outer transaction
                
                records_processed += 1
                
            except Exception as e:
                records_failed += 1
                self.validation_errors.append({
                    "row": index,
                    "error": str(e),
                    "data": row.to_dict()
                })
                self.logger.warning(f"Failed to process row {index}: {e}")
                
                # Rollback only current record
                if not dry_run:
                    try:
                        self.db_session.rollback()
                    except:
                        self.db_session.close()
                        self.db_session = self.db_manager.get_session()
        
        return records_processed, records_failed
    
    def _process_licenses(
        self,
        df: pd.DataFrame,
        validate_schema: bool,
        dry_run: bool
    ) -> Tuple[int, int]:
        """
        Process license records.
        
        Args:
            df: DataFrame with license data
            validate_schema: Whether to validate against schema
            dry_run: If True, don't persist to database
            
        Returns:
            Tuple of (records_processed, records_failed)
        """
        records_processed = 0
        records_failed = 0
        
        for index, row in df.iterrows():
            try:
                # Create savepoint for this record
                if not dry_run:
                    self.db_session.begin_nested()
                
                data = row.where(pd.notna(row), None).to_dict()
                
                # Get client ID
                client_id = data.get('client_id')
                if not client_id and 'client_name' in data:
                    # Use no_autoflush to prevent premature flush
                    with self.db_session.no_autoflush:
                        client = self.db_session.query(Client).filter_by(
                            name=data['client_name']
                        ).first()
                        client_id = client.client_id if client else None
                
                if not client_id:
                    raise ValueError(f"Client not found for row {index}")
                
                # Process license data
                if validate_schema:
                    license_data = LicenseCreate(
                        client_id=client_id,
                        product=data.get('product', 'Unknown'),
                        vendor=data.get('vendor'),
                        license_type=data.get('license_type'),
                        seats_purchased=int(data.get('seats_purchased', 1)),
                        seats_used=int(data.get('seats_used', 0)),
                        cost_per_seat=float(data.get('cost_per_seat', 0)) if data.get('cost_per_seat') else None,
                        total_cost=float(data.get('total_cost', 0)),
                        start_date=pd.to_datetime(data.get('start_date')) if data.get('start_date') else None,
                        end_date=pd.to_datetime(data.get('end_date')) if data.get('end_date') else None,
                        is_active=bool(data.get('is_active', True)),
                        auto_renew=bool(data.get('auto_renew', False)),
                        metadata={}
                    )
                    license_dict = license_data.model_dump()
                else:
                    # Direct processing without validation
                    license_dict = {
                        'client_id': client_id,
                        'product': data.get('product', 'Unknown'),
                        'vendor': data.get('vendor'),
                        'license_type': data.get('license_type'),
                        'seats_purchased': int(data.get('seats_purchased', 1)),
                        'seats_used': int(data.get('seats_used', 0)),
                        'cost_per_seat': float(data.get('cost_per_seat', 0)) if data.get('cost_per_seat') else None,
                        'total_cost': float(data.get('total_cost', 0)),
                        'start_date': pd.to_datetime(data.get('start_date')) if data.get('start_date') else None,
                        'end_date': pd.to_datetime(data.get('end_date')) if data.get('end_date') else None,
                        'is_active': bool(data.get('is_active', True)),
                        'auto_renew': bool(data.get('auto_renew', False)),
                        'metadata_json': {}
                    }
                
                # Save to database if not a dry run
                if not dry_run:
                    license = License(**license_dict)
                    self.db_session.add(license)
                    # Note: Savepoint will be committed with outer transaction
                
                records_processed += 1
                
            except Exception as e:
                records_failed += 1
                self.validation_errors.append({
                    "row": index,
                    "error": str(e),
                    "data": row.to_dict()
                })
                self.logger.warning(f"Failed to process row {index}: {e}")
                
                # Rollback only current record
                if not dry_run:
                    try:
                        self.db_session.rollback()
                    except:
                        self.db_session.close()
                        self.db_session = self.db_manager.get_session()
        
        return records_processed, records_failed
    
    def _create_snapshot(
        self,
        file_path: Path,
        data_type: str,
        actor: str
    ) -> str:
        """
        Create a data snapshot for versioning.
        
        Args:
            file_path: Path to original file
            data_type: Type of data
            actor: User creating snapshot
            
        Returns:
            Snapshot ID
        """
        snapshot_id = str(uuid.uuid4())
        
        # Calculate file checksum
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        checksum = hasher.hexdigest()
        
        # Copy file to snapshots directory
        snapshot_dir = self.config.paths.data_snapshots
        snapshot_path = snapshot_dir / f"{snapshot_id}_{file_path.name}"
        
        import shutil
        shutil.copy2(file_path, snapshot_path)
        
        # Create snapshot record
        snapshot = DataSnapshot(
            snapshot_id=snapshot_id,
            created_by=actor,
            snapshot_type="upload",
            file_path=str(snapshot_path),
            file_size_bytes=file_path.stat().st_size,
            checksum=checksum,
            description=f"Upload of {data_type} data",
            metadata_json={"data_type": data_type, "original_file": str(file_path)}
        )
        self.db_session.add(snapshot)
        
        self.logger.info(f"Created snapshot {snapshot_id}")
        return snapshot_id
    
    def _calculate_confidence_score(
        self,
        records_processed: int,
        records_failed: int,
        validation_errors: int
    ) -> float:
        """
        Calculate confidence score for the processed data.
        
        Args:
            records_processed: Number of successfully processed records
            records_failed: Number of failed records
            validation_errors: Number of validation errors
            
        Returns:
            Confidence score between 0 and 1
        """
        if records_processed == 0:
            return 0.0
        
        success_rate = records_processed / (records_processed + records_failed)
        
        # Penalize for validation errors
        error_penalty = min(validation_errors * 0.05, 0.5)
        
        # Penalize for data quality issues
        quality_penalty = len(self.data_quality_flags) * 0.1
        
        confidence = max(0, min(1, success_rate - error_penalty - quality_penalty))
        
        return round(confidence, 2)
    
    def _log_audit(
        self,
        actor: str,
        action: ActionType,
        target: str,
        success: bool = True,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log audit entry.
        
        Args:
            actor: User or system performing action
            action: Type of action
            target: Resource being acted upon
            success: Whether action succeeded
            error_message: Error message if failed
            details: Additional details
        """
        try:
            audit_entry = AuditLog(
                actor=actor,
                action=action,
                target=target,
                target_type="file",
                success=success,
                error_message=error_message,
                details_json=details or {}
            )
            self.db_session.add(audit_entry)
            self.db_session.commit()
        except Exception as e:
            self.logger.error(f"Failed to log audit entry: {e}")


class DuckDBProcessor:
    """
    Alternative processor using DuckDB for larger datasets.
    
    Provides high-performance processing for large CSV files
    using DuckDB's columnar storage and SQL capabilities.
    """
    
    def __init__(self):
        """Initialize DuckDB processor."""
        self.conn = duckdb.connect(':memory:')
        self.logger = logger.bind(module="duckdb_processor")
    
    def process_large_csv(
        self,
        file_path: Path,
        query: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Process large CSV file using DuckDB.
        
        Args:
            file_path: Path to CSV file
            query: Optional SQL query to run
            
        Returns:
            Processed DataFrame
        """
        try:
            # Read CSV into DuckDB
            self.conn.execute(f"""
                CREATE TABLE temp_data AS 
                SELECT * FROM read_csv_auto('{file_path}')
            """)
            
            # Run query or return all data
            if query:
                result = self.conn.execute(query).fetchdf()
            else:
                result = self.conn.execute("SELECT * FROM temp_data").fetchdf()
            
            # Clean up
            self.conn.execute("DROP TABLE temp_data")
            
            return result
            
        except Exception as e:
            self.logger.error(f"DuckDB processing failed: {e}")
            raise
    
    def aggregate_data(
        self,
        df: pd.DataFrame,
        group_by: List[str],
        aggregations: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Perform aggregations using DuckDB.
        
        Args:
            df: Input DataFrame
            group_by: Columns to group by
            aggregations: Dict of column: aggregation function
            
        Returns:
            Aggregated DataFrame
        """
        # Register DataFrame with DuckDB
        self.conn.register('df', df)
        
        # Build aggregation query
        agg_expr = ", ".join([
            f"{func}({col}) as {col}_{func}"
            for col, func in aggregations.items()
        ])
        group_expr = ", ".join(group_by)
        
        query = f"""
            SELECT {group_expr}, {agg_expr}
            FROM df
            GROUP BY {group_expr}
        """
        
        result = self.conn.execute(query).fetchdf()
        self.conn.unregister('df')
        
        return result
