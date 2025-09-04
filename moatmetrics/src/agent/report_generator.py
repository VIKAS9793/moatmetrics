"""
Report generation module for MoatMetrics.

This module handles the generation of PDF, CSV, and JSON reports
with audit trails and explainable insights.
"""

import json
import csv
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from sqlalchemy.orm import Session
from loguru import logger

from ..utils.database import (
    get_db_manager, Client, Invoice, TimeLog, License,
    AnalyticsResult, AuditLog, ActionType
)
from ..utils.config_loader import get_config


class ReportGenerator:
    """
    Generates reports in various formats with audit trail support.
    
    Supports PDF, CSV, and JSON formats with customizable content
    including analytics results, audit trails, and explanations.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize report generator.
        
        Args:
            db_session: Optional database session
        """
        self.config = get_config()
        self.db_manager = get_db_manager()
        self.db_session = db_session or self.db_manager.get_session()
        self.logger = logger.bind(module="report_generator")
        
    def generate_report(
        self,
        report_type: str,
        format: str = "pdf",
        client_ids: Optional[List[int]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_audit_trail: bool = True,
        include_explanations: bool = True,
        actor: str = "system"
    ) -> Path:
        """
        Generate a report in the specified format.
        
        Args:
            report_type: Type of report (profitability, licenses, spend, summary)
            format: Output format (pdf, csv, json)
            client_ids: Optional list of client IDs to filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            include_audit_trail: Whether to include audit information
            include_explanations: Whether to include AI explanations
            actor: User generating the report
            
        Returns:
            Path to generated report file
        """
        self.logger.info(f"Generating {format} report of type {report_type}")
        
        try:
            # Generate report ID
            report_id = f"RPT-{report_type}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
            
            # Gather data based on report type
            if report_type == "profitability":
                data = self._gather_profitability_data(client_ids, start_date, end_date)
            elif report_type == "licenses":
                data = self._gather_license_data(client_ids)
            elif report_type == "spend":
                data = self._gather_spend_data(client_ids, start_date, end_date)
            elif report_type == "summary":
                data = self._gather_summary_data(client_ids, start_date, end_date)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            # Add audit trail if requested
            if include_audit_trail:
                data["audit_trail"] = self._get_audit_trail(start_date, end_date)
            
            # Add explanations if requested
            if include_explanations:
                data["explanations"] = self._get_explanations(client_ids, start_date, end_date)
            
            # Generate report in specified format
            if format == "pdf":
                report_path = self._generate_pdf(report_id, report_type, data)
            elif format == "csv":
                report_path = self._generate_csv(report_id, report_type, data)
            elif format == "json":
                report_path = self._generate_json(report_id, report_type, data)
            else:
                raise ValueError(f"Unknown format: {format}")
            
            # Log audit entry
            self._log_audit(
                actor=actor,
                action=ActionType.REPORT_GENERATE,
                target=report_id,
                success=True,
                details={
                    "report_type": report_type,
                    "format": format,
                    "client_count": len(client_ids) if client_ids else "all",
                    "file_path": str(report_path)
                }
            )
            
            self.logger.info(f"Report generated successfully: {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            
            # Log failed audit entry
            self._log_audit(
                actor=actor,
                action=ActionType.REPORT_GENERATE,
                target=report_type,
                success=False,
                error_message=str(e)
            )
            
            raise
    
    def _gather_profitability_data(
        self,
        client_ids: Optional[List[int]],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """Gather profitability data for report."""
        # Get clients
        query = self.db_session.query(Client)
        if client_ids:
            query = query.filter(Client.client_id.in_(client_ids))
        clients = query.all()
        
        profitability_data = []
        
        for client in clients:
            # Get invoices
            invoice_query = self.db_session.query(Invoice).filter(
                Invoice.client_id == client.client_id
            )
            if start_date:
                invoice_query = invoice_query.filter(Invoice.date >= start_date)
            if end_date:
                invoice_query = invoice_query.filter(Invoice.date <= end_date)
            
            invoices = invoice_query.all()
            revenue = sum(i.total_amount for i in invoices)
            
            # Get time logs
            time_query = self.db_session.query(TimeLog).filter(
                TimeLog.client_id == client.client_id
            )
            if start_date:
                time_query = time_query.filter(TimeLog.date >= start_date)
            if end_date:
                time_query = time_query.filter(TimeLog.date <= end_date)
            
            time_logs = time_query.all()
            costs = sum(t.total_cost for t in time_logs)
            hours = sum(t.hours for t in time_logs)
            
            profit = revenue - costs
            margin = (profit / revenue * 100) if revenue > 0 else 0
            
            profitability_data.append({
                "client_id": client.client_id,
                "client_name": client.name,
                "industry": client.industry,
                "revenue": revenue,
                "costs": costs,
                "profit": profit,
                "margin_percentage": margin,
                "total_hours": hours,
                "invoice_count": len(invoices)
            })
        
        return {
            "profitability": profitability_data,
            "summary": {
                "total_revenue": sum(d["revenue"] for d in profitability_data),
                "total_costs": sum(d["costs"] for d in profitability_data),
                "total_profit": sum(d["profit"] for d in profitability_data),
                "average_margin": sum(d["margin_percentage"] for d in profitability_data) / len(profitability_data) if profitability_data else 0,
                "client_count": len(profitability_data)
            }
        }
    
    def _gather_license_data(
        self,
        client_ids: Optional[List[int]]
    ) -> Dict[str, Any]:
        """Gather license data for report."""
        query = self.db_session.query(License)
        if client_ids:
            query = query.filter(License.client_id.in_(client_ids))
        
        licenses = query.all()
        
        license_data = []
        for lic in licenses:
            utilization = (lic.seats_used / lic.seats_purchased * 100) if lic.seats_purchased > 0 else 0
            waste = (lic.seats_purchased - lic.seats_used) * (lic.total_cost / lic.seats_purchased) if lic.seats_purchased > 0 else 0
            
            # Get client name
            client = self.db_session.query(Client).filter(
                Client.client_id == lic.client_id
            ).first()
            
            license_data.append({
                "license_id": lic.license_id,
                "client_name": client.name if client else "Unknown",
                "product": lic.product,
                "vendor": lic.vendor,
                "seats_purchased": lic.seats_purchased,
                "seats_used": lic.seats_used,
                "utilization_rate": utilization,
                "total_cost": lic.total_cost,
                "waste_amount": waste,
                "is_active": lic.is_active,
                "auto_renew": lic.auto_renew
            })
        
        return {
            "licenses": license_data,
            "summary": {
                "total_licenses": len(license_data),
                "active_licenses": sum(1 for l in license_data if l["is_active"]),
                "average_utilization": sum(l["utilization_rate"] for l in license_data) / len(license_data) if license_data else 0,
                "total_waste": sum(l["waste_amount"] for l in license_data),
                "underutilized_count": sum(1 for l in license_data if l["utilization_rate"] < 50)
            }
        }
    
    def _gather_spend_data(
        self,
        client_ids: Optional[List[int]],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """Gather spending data for report."""
        # Get invoice spending
        invoice_query = self.db_session.query(Invoice)
        if client_ids:
            invoice_query = invoice_query.filter(Invoice.client_id.in_(client_ids))
        if start_date:
            invoice_query = invoice_query.filter(Invoice.date >= start_date)
        if end_date:
            invoice_query = invoice_query.filter(Invoice.date <= end_date)
        
        invoices = invoice_query.all()
        
        # Group by month
        monthly_spend = {}
        for invoice in invoices:
            month_key = invoice.date.strftime("%Y-%m")
            if month_key not in monthly_spend:
                monthly_spend[month_key] = 0
            monthly_spend[month_key] += invoice.total_amount
        
        # Get license spending
        license_query = self.db_session.query(License)
        if client_ids:
            license_query = license_query.filter(License.client_id.in_(client_ids))
        
        licenses = license_query.all()
        total_license_spend = sum(l.total_cost for l in licenses)
        active_license_spend = sum(l.total_cost for l in licenses if l.is_active)
        
        return {
            "monthly_spend": [
                {"month": k, "amount": v}
                for k, v in sorted(monthly_spend.items())
            ],
            "license_spend": {
                "total": total_license_spend,
                "active": active_license_spend,
                "inactive": total_license_spend - active_license_spend
            },
            "summary": {
                "total_spend": sum(monthly_spend.values()),
                "average_monthly": sum(monthly_spend.values()) / len(monthly_spend) if monthly_spend else 0,
                "months_covered": len(monthly_spend)
            }
        }
    
    def _gather_summary_data(
        self,
        client_ids: Optional[List[int]],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """Gather comprehensive summary data."""
        profitability = self._gather_profitability_data(client_ids, start_date, end_date)
        licenses = self._gather_license_data(client_ids)
        spend = self._gather_spend_data(client_ids, start_date, end_date)
        
        # Get analytics results
        analytics_query = self.db_session.query(AnalyticsResult)
        if client_ids:
            analytics_query = analytics_query.filter(
                AnalyticsResult.client_id.in_(client_ids)
            )
        
        analytics = analytics_query.all()
        
        return {
            "profitability_summary": profitability["summary"],
            "license_summary": licenses["summary"],
            "spend_summary": spend["summary"],
            "analytics_summary": {
                "total_metrics": len(analytics),
                "requiring_review": sum(1 for a in analytics if a.requires_review),
                "average_confidence": sum(a.confidence_score for a in analytics) / len(analytics) if analytics else 0
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_audit_trail(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Get audit trail for report."""
        query = self.db_session.query(AuditLog)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        query = query.order_by(AuditLog.timestamp.desc()).limit(100)
        
        entries = query.all()
        
        return [{
            "timestamp": e.timestamp.isoformat(),
            "actor": e.actor,
            "action": e.action.value if hasattr(e.action, 'value') else str(e.action),
            "target": e.target,
            "success": e.success,
            "error": e.error_message
        } for e in entries]
    
    def _get_explanations(
        self,
        client_ids: Optional[List[int]],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Get AI explanations for analytics results."""
        query = self.db_session.query(AnalyticsResult)
        
        if client_ids:
            query = query.filter(AnalyticsResult.client_id.in_(client_ids))
        
        query = query.filter(AnalyticsResult.explanation.isnot(None)).limit(50)
        
        results = query.all()
        
        return [{
            "metric": r.metric_name,
            "value": r.value,
            "confidence": r.confidence_score,
            "explanation": r.explanation,
            "recommendations": r.recommendations
        } for r in results]
    
    def _generate_pdf(
        self,
        report_id: str,
        report_type: str,
        data: Dict[str, Any]
    ) -> Path:
        """Generate PDF report."""
        report_path = self.config.paths.reports / f"{report_id}.pdf"
        
        doc = SimpleDocTemplate(str(report_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        story.append(Paragraph(f"MoatMetrics {report_type.title()} Report", title_style))
        story.append(Spacer(1, 20))
        
        # Metadata
        story.append(Paragraph(f"Report ID: {report_id}", styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add content based on report type
        if report_type == "profitability" and "profitability" in data:
            story.append(Paragraph("Profitability Analysis", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            # Create table
            table_data = [["Client", "Revenue", "Costs", "Profit", "Margin %"]]
            for item in data["profitability"]:
                table_data.append([
                    item["client_name"],
                    f"${item['revenue']:,.2f}",
                    f"${item['costs']:,.2f}",
                    f"${item['profit']:,.2f}",
                    f"{item['margin_percentage']:.1f}%"
                ])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Summary
            if "summary" in data:
                story.append(Paragraph("Summary", styles['Heading3']))
                summary = data["summary"]
                story.append(Paragraph(f"Total Revenue: ${summary.get('total_revenue', 0):,.2f}", styles['Normal']))
                story.append(Paragraph(f"Total Costs: ${summary.get('total_costs', 0):,.2f}", styles['Normal']))
                story.append(Paragraph(f"Total Profit: ${summary.get('total_profit', 0):,.2f}", styles['Normal']))
                story.append(Paragraph(f"Average Margin: {summary.get('average_margin', 0):.1f}%", styles['Normal']))
        
        elif report_type == "licenses" and "licenses" in data:
            story.append(Paragraph("License Utilization Report", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            # Create table
            table_data = [["Product", "Client", "Purchased", "Used", "Utilization %", "Waste"]]
            for item in data["licenses"]:
                table_data.append([
                    item["product"],
                    item["client_name"],
                    str(item["seats_purchased"]),
                    str(item["seats_used"]),
                    f"{item['utilization_rate']:.1f}%",
                    f"${item['waste_amount']:,.2f}"
                ])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        # Add audit trail if present
        if "audit_trail" in data and data["audit_trail"]:
            story.append(PageBreak())
            story.append(Paragraph("Audit Trail", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            for entry in data["audit_trail"][:10]:  # Limit to 10 entries
                story.append(Paragraph(
                    f"{entry['timestamp']} - {entry['actor']} - {entry['action']} - {'Success' if entry['success'] else 'Failed'}",
                    styles['Normal']
                ))
        
        # Build PDF
        doc.build(story)
        
        return report_path
    
    def _generate_csv(
        self,
        report_id: str,
        report_type: str,
        data: Dict[str, Any]
    ) -> Path:
        """Generate CSV report."""
        report_path = self.config.paths.reports / f"{report_id}.csv"
        
        with open(report_path, 'w', newline='') as csvfile:
            if report_type == "profitability" and "profitability" in data:
                fieldnames = ["client_name", "revenue", "costs", "profit", "margin_percentage"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for item in data["profitability"]:
                    writer.writerow({k: item[k] for k in fieldnames})
            
            elif report_type == "licenses" and "licenses" in data:
                fieldnames = ["product", "client_name", "seats_purchased", "seats_used", "utilization_rate", "waste_amount"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for item in data["licenses"]:
                    writer.writerow({k: item[k] for k in fieldnames})
            
            elif report_type == "spend" and "monthly_spend" in data:
                fieldnames = ["month", "amount"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for item in data["monthly_spend"]:
                    writer.writerow(item)
        
        return report_path
    
    def _generate_json(
        self,
        report_id: str,
        report_type: str,
        data: Dict[str, Any]
    ) -> Path:
        """Generate JSON report."""
        report_path = self.config.paths.reports / f"{report_id}.json"
        
        # Add metadata
        output = {
            "report_id": report_id,
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "data": data
        }
        
        with open(report_path, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        return report_path
    
    def _log_audit(
        self,
        actor: str,
        action: ActionType,
        target: str,
        success: bool = True,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log audit entry."""
        try:
            audit_entry = AuditLog(
                actor=actor,
                action=action,
                target=target,
                target_type="report",
                success=success,
                error_message=error_message,
                details_json=details or {}
            )
            self.db_session.add(audit_entry)
            self.db_session.commit()
        except Exception as e:
            self.logger.error(f"Failed to log audit entry: {e}")
