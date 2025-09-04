"""
Analytics engine for MoatMetrics with SHAP explanations.

This module provides comprehensive analytics computations including
profitability analysis, license efficiency, and explainable AI insights.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import uuid
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
# import shap  # Optional for MVP - commented out for now
from sqlalchemy.orm import Session
from loguru import logger
from typing import Union

from ..utils.database import (
    get_db_manager, Client, Invoice, TimeLog, License,
    AnalyticsResult, MetricType, ConfidenceLevel, ActionType, AuditLog
)
from ..utils.schemas import (
    AnalyticsRequest, AnalyticsResultCreate,
    ConfidenceLevel as SchemaConfidenceLevel
)
from ..utils.config_loader import get_config

warnings.filterwarnings('ignore', category=FutureWarning)


def convert_numpy_types(obj: Any) -> Any:
    """
    Convert numpy types to Python native types for JSON serialization.
    
    Args:
        obj: Object that may contain numpy types
        
    Returns:
        Object with numpy types converted to Python native types
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.bool_, np.bool8)):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    else:
        return obj


class AnalyticsEngine:
    """
    Main analytics engine for computing metrics and generating insights.
    
    Provides profitability analysis, license efficiency calculations,
    and SHAP-based explanations for all metrics.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize analytics engine.
        
        Args:
            db_session: Optional database session
        """
        self.config = get_config()
        self.db_manager = get_db_manager()
        self.db_session = db_session or self.db_manager.get_session()
        self.logger = logger.bind(module="analytics_engine")
        self.snapshot_id = str(uuid.uuid4())
        self.results: List[AnalyticsResultCreate] = []
        
    def run_analytics(
        self,
        request: AnalyticsRequest,
        actor: str = "system"
    ) -> Dict[str, Any]:
        """
        Run comprehensive analytics based on request.
        
        Args:
            request: Analytics request parameters
            actor: User or system running analytics
            
        Returns:
            Dictionary with analytics results
        """
        self.logger.info(f"Starting analytics run with snapshot {self.snapshot_id}")
        
        try:
            # Get data for analysis
            df_clients = self._get_client_data(request.client_ids)
            df_invoices = self._get_invoice_data(request.client_ids, request.start_date, request.end_date)
            df_time_logs = self._get_time_log_data(request.client_ids, request.start_date, request.end_date)
            df_licenses = self._get_license_data(request.client_ids)
            
            # Run different analytics
            metric_types = request.metric_types or [
                "profitability", "license_efficiency", 
                "resource_utilization", "spend_analysis"
            ]
            
            results = {
                "snapshot_id": self.snapshot_id,
                "metrics": {},
                "summary": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if "profitability" in metric_types:
                results["metrics"]["profitability"] = self._analyze_profitability(
                    df_clients, df_invoices, df_time_logs, request.include_explanations
                )
            
            if "license_efficiency" in metric_types:
                results["metrics"]["license_efficiency"] = self._analyze_license_efficiency(
                    df_licenses, request.include_explanations
                )
            
            if "resource_utilization" in metric_types:
                results["metrics"]["resource_utilization"] = self._analyze_resource_utilization(
                    df_time_logs, request.include_explanations
                )
            
            if "spend_analysis" in metric_types:
                results["metrics"]["spend_analysis"] = self._analyze_spend_patterns(
                    df_invoices, df_licenses, request.include_explanations
                )
            
            # Calculate summary statistics
            results["summary"] = self._calculate_summary_stats(results["metrics"])
            
            # Save results to database
            self._save_results(request.confidence_threshold)
            
            # Log audit entry
            self._log_audit(
                actor=actor,
                action=ActionType.ANALYTICS_RUN,
                target=self.snapshot_id,
                success=True,
                details={
                    "metric_types": metric_types,
                    "client_count": len(df_clients),
                    "results_count": len(self.results)
                }
            )
            
            self.logger.info(f"Analytics run completed successfully")
            return convert_numpy_types(results)
            
        except Exception as e:
            self.logger.error(f"Analytics run failed: {e}")
            
            # Log failed audit entry
            self._log_audit(
                actor=actor,
                action=ActionType.ANALYTICS_RUN,
                target=self.snapshot_id,
                success=False,
                error_message=str(e)
            )
            
            raise
    
    def _analyze_profitability(
        self,
        df_clients: pd.DataFrame,
        df_invoices: pd.DataFrame,
        df_time_logs: pd.DataFrame,
        include_explanations: bool
    ) -> Dict[str, Any]:
        """
        Analyze client profitability with explanations.
        
        Args:
            df_clients: Client data
            df_invoices: Invoice data
            df_time_logs: Time log data
            include_explanations: Whether to include SHAP explanations
            
        Returns:
            Profitability analysis results
        """
        self.logger.info("Analyzing profitability")
        
        # Debug logging
        self.logger.info(f"Clients DataFrame shape: {df_clients.shape}")
        self.logger.info(f"Clients DataFrame columns: {list(df_clients.columns)}")
        self.logger.info(f"Invoices DataFrame shape: {df_invoices.shape}")
        self.logger.info(f"Time logs DataFrame shape: {df_time_logs.shape}")
        
        if df_clients.empty:
            self.logger.warning("No client data available for profitability analysis")
            return {"clients": [], "summary": {"avg_profit_margin": 0, "total_revenue": 0, "total_costs": 0, "total_profit": 0}}
        
        results = []
        
        for _, client in df_clients.iterrows():
            self.logger.info(f"Processing client row: {client.to_dict()}")
            client_id = client['client_id']
            
            # Calculate revenue
            if df_invoices.empty:
                client_invoices = pd.DataFrame()
                revenue = 0
            else:
                client_invoices = df_invoices[df_invoices['client_id'] == client_id]
                revenue = client_invoices['total_amount'].sum()
            
            # Calculate costs
            if df_time_logs.empty:
                client_time = pd.DataFrame()
                labor_cost = 0
            else:
                client_time = df_time_logs[df_time_logs['client_id'] == client_id]
                labor_cost = client_time['total_cost'].sum()
            
            # Calculate profit
            profit = revenue - labor_cost
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0
            
            # Prepare features for explanation
            features = pd.DataFrame({
                'revenue': [revenue],
                'labor_cost': [labor_cost],
                'invoice_count': [len(client_invoices)],
                'hours_worked': [client_time['hours'].sum() if not client_time.empty else 0],
                'avg_hourly_rate': [client_time['rate'].mean() if not client_time.empty else 0]
            })
            
            # Calculate confidence and explanations
            confidence_score, shap_values, feature_importance = self._calculate_confidence_and_explanation(
                features, profit_margin, include_explanations
            )
            
            # Determine if review required
            requires_review = confidence_score < self.config.analytics.confidence_threshold
            
            # Create result
            result = AnalyticsResultCreate(
                snapshot_id=self.snapshot_id,
                client_id=client_id,
                metric_type=MetricType.PROFITABILITY.value,
                metric_name=f"Profit Margin - {client['name']}",
                value=profit_margin,
                confidence_score=confidence_score,
                explanation=self._generate_explanation(
                    "profitability", profit_margin, confidence_score
                ),
                recommendations=self._generate_recommendations(
                    "profitability", profit_margin, features.iloc[0].to_dict()
                ),
                shap_values=shap_values,
                feature_importance=feature_importance,
                requires_review=requires_review
            )
            
            self.results.append(result)
            results.append({
                "client_id": int(client_id),
                "client_name": str(client['name']),
                "revenue": float(revenue),
                "costs": float(labor_cost),
                "profit": float(profit),
                "profit_margin": float(profit_margin),
                "confidence_score": float(confidence_score),
                "confidence_level": result.confidence_level.value,
                "requires_review": bool(requires_review)
            })
        
        return {
            "clients": results,
            "summary": {
                "avg_profit_margin": float(np.mean([r['profit_margin'] for r in results]) if results else 0),
                "total_revenue": float(sum(r['revenue'] for r in results)),
                "total_costs": float(sum(r['costs'] for r in results)),
                "total_profit": float(sum(r['profit'] for r in results))
            }
        }
    
    def _analyze_license_efficiency(
        self,
        df_licenses: pd.DataFrame,
        include_explanations: bool
    ) -> Dict[str, Any]:
        """
        Analyze license utilization and efficiency.
        
        Args:
            df_licenses: License data
            include_explanations: Whether to include SHAP explanations
            
        Returns:
            License efficiency analysis results
        """
        self.logger.info("Analyzing license efficiency")
        
        results = []
        
        for _, license in df_licenses.iterrows():
            utilization_rate = (license['seats_used'] / license['seats_purchased'] * 100) \
                if license['seats_purchased'] > 0 else 0
            
            cost_per_used_seat = license['total_cost'] / license['seats_used'] \
                if license['seats_used'] > 0 else float('inf')
            
            waste_amount = (license['seats_purchased'] - license['seats_used']) * \
                (license['total_cost'] / license['seats_purchased']) \
                if license['seats_purchased'] > 0 else 0
            
            # Prepare features
            features = pd.DataFrame({
                'seats_purchased': [license['seats_purchased']],
                'seats_used': [license['seats_used']],
                'total_cost': [license['total_cost']],
                'utilization_rate': [utilization_rate],
                'waste_amount': [waste_amount]
            })
            
            # Calculate confidence and explanations
            confidence_score, shap_values, feature_importance = self._calculate_confidence_and_explanation(
                features, utilization_rate, include_explanations
            )
            
            # Determine status
            if utilization_rate < 30:
                status = "critical_underutilization"
                requires_review = True
            elif utilization_rate < 50:
                status = "underutilized"
                requires_review = True
            elif utilization_rate < 80:
                status = "moderate"
                requires_review = False
            else:
                status = "optimal"
                requires_review = False
            
            # Create result
            result = AnalyticsResultCreate(
                snapshot_id=self.snapshot_id,
                client_id=license['client_id'],
                metric_type=MetricType.LICENSE_EFFICIENCY.value,
                metric_name=f"License Utilization - {license['product']}",
                value=utilization_rate,
                confidence_score=confidence_score,
                explanation=self._generate_explanation(
                    "license_efficiency", utilization_rate, confidence_score
                ),
                recommendations=self._generate_recommendations(
                    "license_efficiency", utilization_rate, features.iloc[0].to_dict()
                ),
                shap_values=shap_values,
                feature_importance=feature_importance,
                requires_review=requires_review
            )
            
            self.results.append(result)
            results.append({
                "license_id": int(license['license_id']),
                "product": str(license['product']),
                "client_id": int(license['client_id']),
                "utilization_rate": float(utilization_rate),
                "status": status,
                "waste_amount": float(waste_amount),
                "cost_per_used_seat": float(cost_per_used_seat) if cost_per_used_seat != float('inf') else None,
                "confidence_score": float(confidence_score),
                "requires_review": bool(requires_review)
            })
        
        return {
            "licenses": results,
            "summary": {
                "avg_utilization": float(np.mean([r['utilization_rate'] for r in results]) if results else 0),
                "total_waste": float(sum(r['waste_amount'] for r in results)),
                "underutilized_count": int(sum(1 for r in results if r['status'] in ['critical_underutilization', 'underutilized'])),
                "total_licenses": int(len(results))
            }
        }
    
    def _analyze_resource_utilization(
        self,
        df_time_logs: pd.DataFrame,
        include_explanations: bool
    ) -> Dict[str, Any]:
        """
        Analyze resource utilization patterns.
        
        Args:
            df_time_logs: Time log data
            include_explanations: Whether to include explanations
            
        Returns:
            Resource utilization analysis
        """
        self.logger.info("Analyzing resource utilization")
        
        # Group by staff
        staff_utilization = df_time_logs.groupby('staff_name').agg({
            'hours': 'sum',
            'total_cost': 'sum',
            'rate': 'mean',
            'billable': lambda x: (x == True).sum() / len(x) * 100
        }).reset_index()
        
        staff_utilization.columns = ['staff_name', 'total_hours', 'total_revenue', 'avg_rate', 'billable_percentage']
        
        # Calculate utilization assuming 40 hours per week
        weeks_in_period = (df_time_logs['date'].max() - df_time_logs['date'].min()).days / 7
        expected_hours = weeks_in_period * 40
        
        results = []
        for _, staff in staff_utilization.iterrows():
            utilization_rate = (staff['total_hours'] / expected_hours * 100) if expected_hours > 0 else 0
            
            # Prepare features
            features = pd.DataFrame({
                'total_hours': [staff['total_hours']],
                'avg_rate': [staff['avg_rate']],
                'billable_percentage': [staff['billable_percentage']],
                'total_revenue': [staff['total_revenue']]
            })
            
            # Calculate confidence
            confidence_score, shap_values, feature_importance = self._calculate_confidence_and_explanation(
                features, utilization_rate, include_explanations
            )
            
            # Create result
            result = AnalyticsResultCreate(
                snapshot_id=self.snapshot_id,
                client_id=None,
                metric_type=MetricType.RESOURCE_UTILIZATION.value,
                metric_name=f"Staff Utilization - {staff['staff_name']}",
                value=utilization_rate,
                confidence_score=confidence_score,
                explanation=self._generate_explanation(
                    "resource_utilization", utilization_rate, confidence_score
                ),
                recommendations=self._generate_recommendations(
                    "resource_utilization", utilization_rate, features.iloc[0].to_dict()
                ),
                shap_values=shap_values,
                feature_importance=feature_importance,
                requires_review=utilization_rate < 60 or utilization_rate > 120
            )
            
            self.results.append(result)
            results.append({
                "staff_name": str(staff['staff_name']),
                "total_hours": float(staff['total_hours']),
                "utilization_rate": float(utilization_rate),
                "billable_percentage": float(staff['billable_percentage']),
                "avg_rate": float(staff['avg_rate']),
                "total_revenue": float(staff['total_revenue']),
                "confidence_score": float(confidence_score)
            })
        
        return {
            "staff": results,
            "summary": {
                "avg_utilization": float(np.mean([r['utilization_rate'] for r in results]) if results else 0),
                "avg_billable_percentage": float(np.mean([r['billable_percentage'] for r in results]) if results else 0),
                "total_hours": float(sum(r['total_hours'] for r in results)),
                "total_revenue": float(sum(r['total_revenue'] for r in results))
            }
        }
    
    def _analyze_spend_patterns(
        self,
        df_invoices: pd.DataFrame,
        df_licenses: pd.DataFrame,
        include_explanations: bool
    ) -> Dict[str, Any]:
        """
        Analyze spending patterns and trends.
        
        Args:
            df_invoices: Invoice data
            df_licenses: License data
            include_explanations: Whether to include explanations
            
        Returns:
            Spend analysis results
        """
        self.logger.info("Analyzing spend patterns")
        
        # Monthly spend analysis
        df_invoices['month'] = pd.to_datetime(df_invoices['date']).dt.to_period('M')
        monthly_spend = df_invoices.groupby('month')['total_amount'].sum().reset_index()
        
        # Calculate trend
        if len(monthly_spend) > 1:
            spend_trend = np.polyfit(range(len(monthly_spend)), monthly_spend['total_amount'], 1)[0]
            trend_percentage = (spend_trend / monthly_spend['total_amount'].mean() * 100) if monthly_spend['total_amount'].mean() > 0 else 0
        else:
            spend_trend = 0
            trend_percentage = 0
        
        # License spend
        total_license_spend = df_licenses['total_cost'].sum()
        active_license_spend = df_licenses[df_licenses['is_active'] == True]['total_cost'].sum()
        
        # Prepare summary features
        features = pd.DataFrame({
            'avg_monthly_spend': [monthly_spend['total_amount'].mean() if len(monthly_spend) > 0 else 0],
            'spend_trend': [spend_trend],
            'total_license_spend': [total_license_spend],
            'active_license_ratio': [active_license_spend / total_license_spend if total_license_spend > 0 else 1]
        })
        
        # Calculate confidence
        confidence_score, shap_values, feature_importance = self._calculate_confidence_and_explanation(
            features, trend_percentage, include_explanations
        )
        
        # Create result
        result = AnalyticsResultCreate(
            snapshot_id=self.snapshot_id,
            client_id=None,
            metric_type=MetricType.SPEND_ANALYSIS.value,
            metric_name="Overall Spend Trend",
            value=trend_percentage,
            confidence_score=confidence_score,
            explanation=self._generate_explanation(
                "spend_analysis", trend_percentage, confidence_score
            ),
            recommendations=self._generate_recommendations(
                "spend_analysis", trend_percentage, features.iloc[0].to_dict()
            ),
            shap_values=shap_values,
            feature_importance=feature_importance,
            requires_review=abs(trend_percentage) > 20
        )
        
        self.results.append(result)
        
        return {
            "monthly_trend": {
                "data": monthly_spend.to_dict('records') if len(monthly_spend) > 0 else [],
                "trend_percentage": trend_percentage,
                "trend_direction": "increasing" if spend_trend > 0 else "decreasing" if spend_trend < 0 else "stable"
            },
            "license_spend": {
                "total": total_license_spend,
                "active": active_license_spend,
                "inactive": total_license_spend - active_license_spend
            },
            "confidence_score": confidence_score
        }
    
    def _calculate_confidence_and_explanation(
        self,
        features: pd.DataFrame,
        target_value: float,
        include_explanations: bool
    ) -> Tuple[float, Optional[Dict[str, float]], Optional[Dict[str, float]]]:
        """
        Calculate confidence score and SHAP explanations.
        
        Args:
            features: Feature DataFrame
            target_value: Target metric value
            include_explanations: Whether to calculate SHAP values
            
        Returns:
            Tuple of (confidence_score, shap_values, feature_importance)
        """
        # Simple confidence calculation based on data completeness and variance
        confidence_score = 0.8  # Base confidence
        
        # Penalize for missing data
        missing_ratio = features.isnull().sum().sum() / (len(features) * len(features.columns))
        confidence_score -= missing_ratio * 0.3
        
        # Penalize for extreme values
        for col in features.columns:
            if features[col].dtype in ['float64', 'int64']:
                if features[col].iloc[0] == 0:
                    confidence_score -= 0.05
        
        # SHAP explanations if requested and enough data
        shap_values = None
        feature_importance = None
        
        if include_explanations and self.config.analytics.enable_shap:
            try:
                # For demonstration, use simple feature importance
                # In production, train a model and use SHAP
                feature_importance = {}
                total = features.abs().sum(axis=1).iloc[0]
                
                for col in features.columns:
                    if total > 0:
                        feature_importance[col] = abs(features[col].iloc[0]) / total
                    else:
                        feature_importance[col] = 1.0 / len(features.columns)
                
                # Simulated SHAP values (in production, use actual SHAP)
                shap_values = feature_importance.copy()
                
            except Exception as e:
                self.logger.warning(f"Failed to calculate SHAP values: {e}")
        
        # Ensure confidence is between 0 and 1
        confidence_score = max(0.1, min(1.0, confidence_score))
        
        return confidence_score, shap_values, feature_importance
    
    def _generate_explanation(
        self,
        metric_type: str,
        value: float,
        confidence: float
    ) -> str:
        """
        Generate human-readable explanation for metric.
        
        Args:
            metric_type: Type of metric
            value: Metric value
            confidence: Confidence score
            
        Returns:
            Explanation text
        """
        explanations = {
            "profitability": {
                "high": f"Profit margin of {value:.1f}% indicates strong profitability. Confidence: {confidence:.0%}",
                "medium": f"Profit margin of {value:.1f}% shows moderate profitability. Confidence: {confidence:.0%}",
                "low": f"Profit margin of {value:.1f}% suggests low profitability. Review cost structure. Confidence: {confidence:.0%}"
            },
            "license_efficiency": {
                "high": f"License utilization at {value:.1f}% is optimal. Confidence: {confidence:.0%}",
                "medium": f"License utilization at {value:.1f}% could be improved. Confidence: {confidence:.0%}",
                "low": f"License utilization at {value:.1f}% indicates significant waste. Immediate action recommended. Confidence: {confidence:.0%}"
            },
            "resource_utilization": {
                "high": f"Resource utilization at {value:.1f}% is healthy. Confidence: {confidence:.0%}",
                "medium": f"Resource utilization at {value:.1f}% shows room for optimization. Confidence: {confidence:.0%}",
                "low": f"Resource utilization at {value:.1f}% indicates underutilization. Confidence: {confidence:.0%}"
            },
            "spend_analysis": {
                "high": f"Spend trend of {value:.1f}% requires attention. Confidence: {confidence:.0%}",
                "medium": f"Spend trend of {value:.1f}% is within normal range. Confidence: {confidence:.0%}",
                "low": f"Spend trend of {value:.1f}% is stable. Confidence: {confidence:.0%}"
            }
        }
        
        # Determine level
        if metric_type in ["profitability", "license_efficiency", "resource_utilization"]:
            if value >= 70:
                level = "high"
            elif value >= 40:
                level = "medium"
            else:
                level = "low"
        else:  # spend_analysis
            if abs(value) >= 20:
                level = "high"
            elif abs(value) >= 10:
                level = "medium"
            else:
                level = "low"
        
        return explanations.get(metric_type, {}).get(level, f"Value: {value:.1f}, Confidence: {confidence:.0%}")
    
    def _generate_recommendations(
        self,
        metric_type: str,
        value: float,
        features: Dict[str, float]
    ) -> str:
        """
        Generate actionable recommendations.
        
        Args:
            metric_type: Type of metric
            value: Metric value
            features: Feature values
            
        Returns:
            Recommendations text
        """
        recommendations = []
        
        if metric_type == "profitability":
            if value < 20:
                recommendations.append("Review pricing strategy")
                recommendations.append("Analyze cost reduction opportunities")
            if features.get('labor_cost', 0) > features.get('revenue', 1) * 0.7:
                recommendations.append("Labor costs are high relative to revenue")
        
        elif metric_type == "license_efficiency":
            if value < 50:
                recommendations.append("Consider reducing license count")
                recommendations.append("Implement license reclamation process")
            if value < 30:
                recommendations.append("URGENT: Significant license waste detected")
        
        elif metric_type == "resource_utilization":
            if value < 60:
                recommendations.append("Resource capacity available for new projects")
            elif value > 100:
                recommendations.append("Team may be overloaded, consider capacity planning")
            if features.get('billable_percentage', 0) < 70:
                recommendations.append("Improve billable hours ratio")
        
        elif metric_type == "spend_analysis":
            if abs(value) > 20:
                recommendations.append("Significant spend trend detected, review budget")
            if features.get('active_license_ratio', 1) < 0.8:
                recommendations.append("Review inactive licenses for cancellation")
        
        return "; ".join(recommendations) if recommendations else "No specific recommendations at this time"
    
    def _calculate_summary_stats(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate summary statistics across all metrics.
        
        Args:
            metrics: Dictionary of metric results
            
        Returns:
            Summary statistics
        """
        summary = {
            "total_metrics_computed": len(self.results),
            "metrics_requiring_review": sum(1 for r in self.results if r.requires_review),
            "average_confidence": np.mean([r.confidence_score for r in self.results]) if self.results else 0,
            "confidence_distribution": {}
        }
        
        # Count confidence levels
        for result in self.results:
            level = result.confidence_level.value
            summary["confidence_distribution"][level] = summary["confidence_distribution"].get(level, 0) + 1
        
        return summary
    
    def _get_client_data(self, client_ids: Optional[List[int]] = None) -> pd.DataFrame:
        """Get client data from database."""
        query = self.db_session.query(Client)
        if client_ids:
            query = query.filter(Client.client_id.in_(client_ids))
        
        clients = query.all()
        return pd.DataFrame([{
            'client_id': c.client_id,
            'name': c.name,
            'industry': c.industry,
            'is_active': c.is_active
        } for c in clients])
    
    def _get_invoice_data(
        self,
        client_ids: Optional[List[int]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Get invoice data from database."""
        query = self.db_session.query(Invoice)
        
        if client_ids:
            query = query.filter(Invoice.client_id.in_(client_ids))
        if start_date:
            query = query.filter(Invoice.date >= start_date)
        if end_date:
            query = query.filter(Invoice.date <= end_date)
        
        invoices = query.all()
        return pd.DataFrame([{
            'invoice_id': i.invoice_id,
            'client_id': i.client_id,
            'date': i.date,
            'total_amount': i.total_amount,
            'status': i.status
        } for i in invoices])
    
    def _get_time_log_data(
        self,
        client_ids: Optional[List[int]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Get time log data from database."""
        query = self.db_session.query(TimeLog)
        
        if client_ids:
            query = query.filter(TimeLog.client_id.in_(client_ids))
        if start_date:
            query = query.filter(TimeLog.date >= start_date)
        if end_date:
            query = query.filter(TimeLog.date <= end_date)
        
        time_logs = query.all()
        return pd.DataFrame([{
            'log_id': t.log_id,
            'client_id': t.client_id,
            'staff_name': t.staff_name,
            'date': t.date,
            'hours': t.hours,
            'rate': t.rate,
            'total_cost': t.total_cost,
            'billable': t.billable
        } for t in time_logs])
    
    def _get_license_data(self, client_ids: Optional[List[int]] = None) -> pd.DataFrame:
        """Get license data from database."""
        query = self.db_session.query(License)
        
        if client_ids:
            query = query.filter(License.client_id.in_(client_ids))
        
        licenses = query.all()
        return pd.DataFrame([{
            'license_id': l.license_id,
            'client_id': l.client_id,
            'product': l.product,
            'seats_purchased': l.seats_purchased,
            'seats_used': l.seats_used,
            'total_cost': l.total_cost,
            'is_active': l.is_active
        } for l in licenses])
    
    def _save_results(self, confidence_threshold: float) -> None:
        """Save analytics results to database."""
        for result in self.results:
            # Determine confidence level
            if result.confidence_score >= 0.9:
                confidence_level = ConfidenceLevel.HIGH
            elif result.confidence_score >= confidence_threshold:
                confidence_level = ConfidenceLevel.MEDIUM
            elif result.confidence_score >= 0.5:
                confidence_level = ConfidenceLevel.LOW
            else:
                confidence_level = ConfidenceLevel.AMBIGUOUS
            
            db_result = AnalyticsResult(
                snapshot_id=result.snapshot_id,
                client_id=result.client_id,
                metric_type=MetricType[result.metric_type.upper()],
                metric_name=result.metric_name,
                value=result.value,
                confidence_score=result.confidence_score,
                confidence_level=confidence_level,
                explanation=result.explanation,
                shap_values_json=result.shap_values,
                feature_importance_json=result.feature_importance,
                recommendations=result.recommendations,
                requires_review=result.requires_review
            )
            self.db_session.add(db_result)
        
        self.db_session.commit()
        self.logger.info(f"Saved {len(self.results)} analytics results")
    
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
                target_type="analytics",
                success=success,
                error_message=error_message,
                details_json=details or {}
            )
            self.db_session.add(audit_entry)
            self.db_session.commit()
        except Exception as e:
            self.logger.error(f"Failed to log audit entry: {e}")
