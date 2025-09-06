"""
AI Analytics Integration Bridge
Seamlessly integrates AI natural language capabilities with existing analytics engine
"""
from typing import Dict, List, Any, Optional, Union
from loguru import logger
from datetime import datetime

from ..ai.nl_analytics import NaturalLanguageAnalytics, AnalyticsContext, QueryResult
from ..ai.enhanced_nl_analytics import EnhancedNaturalLanguageAnalytics, EnhancedQueryResult
from .engine import AnalyticsEngine
from ..utils.database import get_db_manager


class AIAnalyticsIntegration:
    """Bridge between AI Analytics and existing Analytics Engine"""
    
    def __init__(self, analytics_engine: AnalyticsEngine, 
                 nl_analytics: Optional[NaturalLanguageAnalytics] = None,
                 enhanced_analytics: Optional[EnhancedNaturalLanguageAnalytics] = None):
        self.analytics_engine = analytics_engine
        self.nl_analytics = nl_analytics
        self.enhanced_analytics = enhanced_analytics
        self.db_manager = get_db_manager()
        
        logger.info("AI Analytics Integration Bridge initialized")
    
    def is_ai_available(self) -> bool:
        """Check if AI analytics components are available"""
        return self.nl_analytics is not None
    
    def is_enhanced_ai_available(self) -> bool:
        """Check if enhanced AI analytics components are available"""
        return self.enhanced_analytics is not None
    
    async def create_analytics_context_from_engine(self) -> AnalyticsContext:
        """Create AI analytics context from current database state via analytics engine"""
        try:
            # Get data through analytics engine which already handles database queries
            clients = await self._get_clients_data()
            invoices = await self._get_invoices_data()
            time_logs = await self._get_time_logs_data()
            licenses = await self._get_licenses_data()
            
            # Calculate summary statistics using analytics engine methods
            summary_stats = await self._calculate_summary_stats(clients, invoices, time_logs, licenses)
            
            return AnalyticsContext(
                clients=clients,
                invoices=invoices,
                time_logs=time_logs,
                licenses=licenses,
                summary_stats=summary_stats
            )
            
        except Exception as e:
            logger.error(f"Error creating analytics context: {e}")
            # Return empty context as fallback
            return AnalyticsContext(
                clients=[], invoices=[], time_logs=[], licenses=[], summary_stats={}
            )
    
    async def _get_clients_data(self) -> List[Dict[str, Any]]:
        """Get clients data formatted for AI analytics"""
        try:
            db = self.db_manager.get_session()
            from ..utils.database import Client
            
            clients = db.query(Client).all()
            
            return [
                {
                    "id": client.client_id,
                    "name": client.name,
                    "industry": getattr(client, 'industry', 'Unknown'),
                    "status": getattr(client, 'status', 'Active'),
                    "contract_value": getattr(client, 'contract_value', 0),
                    "created_date": getattr(client, 'created_date', datetime.now()).isoformat()
                }
                for client in clients
            ]
            
        except Exception as e:
            logger.error(f"Error getting clients data: {e}")
            return []
    
    async def _get_invoices_data(self) -> List[Dict[str, Any]]:
        """Get invoices data formatted for AI analytics"""
        try:
            db = self.db_manager.get_session()
            from ..utils.database import Invoice
            
            invoices = db.query(Invoice).all()
            
            return [
                {
                    "invoice_id": invoice.invoice_id,
                    "client_id": invoice.client_id,
                    "amount": invoice.amount,
                    "cost": getattr(invoice, 'cost', 0),
                    "date": invoice.date.isoformat() if invoice.date else datetime.now().isoformat(),
                    "status": getattr(invoice, 'status', 'Paid'),
                    "type": getattr(invoice, 'service_type', 'General')
                }
                for invoice in invoices
            ]
            
        except Exception as e:
            logger.error(f"Error getting invoices data: {e}")
            return []
    
    async def _get_time_logs_data(self) -> List[Dict[str, Any]]:
        """Get time logs data formatted for AI analytics"""
        try:
            db = self.db_manager.get_session()
            from ..utils.database import TimeLog
            
            time_logs = db.query(TimeLog).all()
            
            return [
                {
                    "log_id": time_log.log_id,
                    "client_id": time_log.client_id,
                    "staff_name": time_log.staff_name,
                    "hours": time_log.hours_worked,
                    "billable": getattr(time_log, 'billable', True),
                    "rate": getattr(time_log, 'hourly_rate', 0),
                    "date": time_log.date.isoformat() if time_log.date else datetime.now().isoformat(),
                    "project": getattr(time_log, 'project', 'General'),
                    "task_type": getattr(time_log, 'task_type', 'Support')
                }
                for time_log in time_logs
            ]
            
        except Exception as e:
            logger.error(f"Error getting time logs data: {e}")
            return []
    
    async def _get_licenses_data(self) -> List[Dict[str, Any]]:
        """Get licenses data formatted for AI analytics"""
        try:
            db = self.db_manager.get_session()
            from ..utils.database import License
            
            licenses = db.query(License).all()
            
            return [
                {
                    "license_id": license.license_id,
                    "product": license.product_name,
                    "seats_purchased": license.seats_purchased,
                    "seats_used": license.seats_used,
                    "cost": license.monthly_cost,
                    "utilization": license.seats_used / max(license.seats_purchased, 1),
                    "vendor": getattr(license, 'vendor', 'Unknown'),
                    "renewal_date": getattr(license, 'renewal_date', datetime.now()).isoformat()
                }
                for license in licenses
            ]
            
        except Exception as e:
            logger.error(f"Error getting licenses data: {e}")
            return []
    
    async def _calculate_summary_stats(self, clients: List[Dict], invoices: List[Dict], 
                                     time_logs: List[Dict], licenses: List[Dict]) -> Dict[str, Any]:
        """Calculate summary statistics for AI context"""
        try:
            # Revenue and cost calculations
            total_revenue = sum(invoice.get('amount', 0) for invoice in invoices)
            total_costs = sum(invoice.get('cost', 0) for invoice in invoices)
            profit_margin = (total_revenue - total_costs) / total_revenue if total_revenue > 0 else 0
            
            # Time and utilization calculations
            total_hours = sum(log.get('hours', 0) for log in time_logs)
            billable_hours = sum(log.get('hours', 0) for log in time_logs if log.get('billable', True))
            utilization_rate = billable_hours / total_hours if total_hours > 0 else 0
            
            # Staff calculations
            unique_staff = set(log.get('staff_name', '') for log in time_logs)
            staff_count = len(unique_staff)
            
            # License calculations
            license_cost = sum(license.get('cost', 0) for license in licenses)
            avg_license_util = sum(
                license.get('utilization', 0) for license in licenses
            ) / len(licenses) if licenses else 0
            
            underutilized_licenses = sum(
                1 for license in licenses if license.get('utilization', 0) < 0.7
            )
            
            return {
                "total_revenue": total_revenue,
                "total_costs": total_costs,
                "profit_margin": profit_margin,
                "total_clients": len(clients),
                "active_clients": len([c for c in clients if c.get('status') == 'Active']),
                "staff_count": staff_count,
                "total_hours": total_hours,
                "billable_hours": billable_hours,
                "utilization_rate": utilization_rate,
                "total_licenses": len(licenses),
                "license_cost": license_cost,
                "avg_license_util": avg_license_util,
                "underutilized_licenses": underutilized_licenses,
                "avg_revenue_per_client": total_revenue / len(clients) if clients else 0,
                "avg_hours_per_client": total_hours / len(clients) if clients else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating summary stats: {e}")
            return {}
    
    async def process_natural_language_query(self, query: str, 
                                           enhanced: bool = False,
                                           urgency: str = "normal",
                                           privacy_level: str = "standard",
                                           enable_ensemble: bool = False) -> Dict[str, Any]:
        """
        Process natural language query using AI analytics
        Returns standardized response format
        """
        if not self.is_ai_available():
            return {
                "success": False,
                "error": "AI Analytics not available",
                "message": "Natural language processing requires AI components to be initialized"
            }
        
        try:
            # Create analytics context from current data
            context = await self.create_analytics_context_from_engine()
            
            # Process query with appropriate AI service
            if enhanced and self.is_enhanced_ai_available():
                result = await self.enhanced_analytics.process_query_enhanced(
                    query=query,
                    context=context,
                    urgency=urgency,
                    privacy_level=privacy_level,
                    enable_ensemble=enable_ensemble
                )
                
                # Convert enhanced result to standard format
                return {
                    "success": True,
                    "answer": result.answer,
                    "confidence": result.confidence,
                    "insights": result.insights,
                    "recommendations": result.recommendations,
                    "processing_time": result.processing_time,
                    "model_used": result.model_used,
                    "data_sources": result.data_sources,
                    "enhanced_metrics": {
                        "optimization_applied": result.optimization_applied,
                        "cache_hit": result.cache_hit,
                        "security_score": result.security_score,
                        "quality_score": result.quality_score,
                        "uncertainty_bounds": list(result.uncertainty_bounds),
                        "ensemble_agreement": result.ensemble_agreement
                    }
                }
                
            else:
                result = await self.nl_analytics.process_query(
                    query=query,
                    context=context,
                    urgency=urgency
                )
                
                return {
                    "success": True,
                    "answer": result.answer,
                    "confidence": result.confidence,
                    "insights": result.insights,
                    "recommendations": result.recommendations,
                    "processing_time": result.processing_time,
                    "model_used": "tinyllama",
                    "data_sources": result.data_sources
                }
                
        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process natural language query"
            }
    
    async def augment_analytics_results(self, analytics_results: Dict[str, Any],
                                      generate_insights: bool = True) -> Dict[str, Any]:
        """
        Augment traditional analytics results with AI-generated insights
        """
        if not self.is_ai_available() or not generate_insights:
            return analytics_results
        
        try:
            # Generate contextual insights based on analytics results
            context = await self.create_analytics_context_from_engine()
            
            # Create summary query based on results
            summary_query = self._create_summary_query_from_results(analytics_results)
            
            if summary_query:
                ai_insights = await self.nl_analytics.process_query(
                    query=summary_query,
                    context=context,
                    urgency="normal"
                )
                
                # Add AI insights to results
                analytics_results["ai_insights"] = {
                    "summary": ai_insights.answer,
                    "key_findings": ai_insights.insights,
                    "recommendations": ai_insights.recommendations,
                    "confidence": ai_insights.confidence,
                    "processing_time": ai_insights.processing_time
                }
                
            return analytics_results
            
        except Exception as e:
            logger.error(f"Error augmenting analytics results: {e}")
            return analytics_results
    
    def _create_summary_query_from_results(self, results: Dict[str, Any]) -> Optional[str]:
        """Create a natural language query based on analytics results"""
        try:
            metrics = results.get('metrics', [])
            if not metrics:
                return None
            
            # Identify key metrics
            profitability_metrics = [m for m in metrics if 'profit' in m.get('metric_name', '').lower()]
            utilization_metrics = [m for m in metrics if 'utilization' in m.get('metric_name', '').lower()]
            license_metrics = [m for m in metrics if 'license' in m.get('metric_name', '').lower()]
            
            # Generate appropriate summary query
            if profitability_metrics:
                return "What do the current profitability metrics tell us about our business performance and what should we focus on?"
            elif utilization_metrics:
                return "How is our team utilization looking and what can we do to improve efficiency?"
            elif license_metrics:
                return "What insights do you have about our software license usage and potential optimizations?"
            else:
                return "Based on the current analytics results, what are the key business insights and recommendations?"
                
        except Exception as e:
            logger.error(f"Error creating summary query: {e}")
            return None
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including AI integration"""
        status = {
            "analytics_engine": "operational",
            "ai_integration": "initialized",
            "natural_language_analytics": self.is_ai_available(),
            "enhanced_ai_analytics": self.is_enhanced_ai_available(),
            "database_connection": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Get AI system info if available
        if self.is_ai_available():
            try:
                ai_info = self.nl_analytics.get_system_info()
                status["ai_system_info"] = ai_info
            except Exception as e:
                logger.error(f"Error getting AI system info: {e}")
                status["ai_system_error"] = str(e)
        
        return status
    
    async def cleanup(self):
        """Cleanup AI integration resources"""
        logger.info("Cleaning up AI Analytics Integration Bridge...")
        
        try:
            if self.enhanced_analytics:
                await self.enhanced_analytics.cleanup()
        except Exception as e:
            logger.error(f"Error during AI integration cleanup: {e}")
        
        logger.info("AI Analytics Integration cleanup completed")


# Factory function to create integration instance
async def create_ai_integration(analytics_engine: AnalyticsEngine) -> AIAnalyticsIntegration:
    """Create AI integration instance with proper component initialization"""
    try:
        # Try to import and initialize AI components
        from ..ai.memory_manager import AIMemoryManager
        from ..ai.nl_analytics import NaturalLanguageAnalytics
        from ..ai.enhanced_nl_analytics import EnhancedNaturalLanguageAnalytics
        
        # Initialize memory manager
        memory_manager = AIMemoryManager()
        await memory_manager.initialize()
        
        # Initialize analytics components
        nl_analytics = NaturalLanguageAnalytics(memory_manager)
        enhanced_analytics = EnhancedNaturalLanguageAnalytics(memory_manager)
        await enhanced_analytics.initialize()
        
        integration = AIAnalyticsIntegration(
            analytics_engine=analytics_engine,
            nl_analytics=nl_analytics,
            enhanced_analytics=enhanced_analytics
        )
        
        logger.success("AI Analytics Integration created successfully")
        return integration
        
    except Exception as e:
        logger.error(f"Failed to create AI integration: {e}")
        # Return integration without AI components
        return AIAnalyticsIntegration(analytics_engine=analytics_engine)
