"""
MoatMetrics Natural Language Analytics Service
Production-grade NLP for MSP analytics with memory-aware processing
"""
import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from .memory_manager import AIMemoryManager


@dataclass
class AnalyticsContext:
    """Analytics context for NLP queries"""
    clients: List[Dict]
    invoices: List[Dict]
    time_logs: List[Dict]
    licenses: List[Dict]
    summary_stats: Dict[str, Any]


@dataclass
class QueryResult:
    """Natural language query result with confidence"""
    answer: str
    confidence: float
    insights: List[str]
    recommendations: List[str]
    data_sources: List[str]
    processing_time: float


class NaturalLanguageAnalytics:
    """Natural language processing for MSP analytics"""
    
    def __init__(self, memory_manager: AIMemoryManager):
        self.memory_manager = memory_manager
        self.query_templates = self._load_query_templates()
        self.context_cache: Optional[AnalyticsContext] = None
        self.cache_timestamp: float = 0
        self.cache_ttl: float = 300  # 5 minutes
        
        logger.info("Natural Language Analytics service initialized")
    
    def _load_query_templates(self) -> Dict[str, str]:
        """Load pre-defined query templates for common MSP questions"""
        return {
            "profitability": """
            Analyze client profitability data and provide insights.
            
            Data Context: {data_context}
            
            Query: {query}
            
            Please provide:
            1. Direct answer to the profitability question
            2. Top 3 most profitable clients
            3. Top 3 least profitable clients (potential risks)
            4. Key trends and patterns
            5. Actionable recommendations for improvement
            6. Confidence level (0.1-1.0) with reasoning
            
            Format response as structured insights for MSP executives.
            """,
            
            "license_efficiency": """
            Analyze software license utilization and efficiency.
            
            Data Context: {data_context}
            
            Query: {query}
            
            Please provide:
            1. Direct answer to the license question
            2. Most underutilized licenses (waste opportunities)
            3. Most efficiently used licenses
            4. Cost savings potential in dollars
            5. Optimization recommendations
            6. Confidence level (0.1-1.0) with reasoning
            
            Focus on actionable cost reduction opportunities.
            """,
            
            "resource_utilization": """
            Analyze staff and resource utilization patterns.
            
            Data Context: {data_context}
            
            Query: {query}
            
            Please provide:
            1. Direct answer to the resource question
            2. Staff utilization rates by person
            3. Capacity planning insights
            4. Productivity improvement opportunities
            5. Workload optimization recommendations
            6. Confidence level (0.1-1.0) with reasoning
            
            Focus on operational efficiency improvements.
            """,
            
            "general_analytics": """
            You are MoatMetrics AI, an expert MSP analytics assistant.
            
            Available MSP Data: {data_context}
            
            User Query: {query}
            
            Please provide:
            1. Direct, accurate answer to the question
            2. Key insights and business implications
            3. Data-driven recommendations
            4. Relevant trends or patterns
            5. Confidence level (0.1-1.0) and reasoning
            
            Keep response focused on MSP business operations and metrics.
            """
        }
    
    def _prepare_data_context(self, context: AnalyticsContext) -> str:
        """Prepare data context for LLM consumption"""
        try:
            # Create compact data summary
            summary = {
                "clients": {
                    "total_count": len(context.clients),
                    "sample": context.clients[:3] if context.clients else [],
                    "industries": list(set(c.get('industry', 'Unknown') for c in context.clients))[:5]
                },
                "financial": {
                    "total_revenue": context.summary_stats.get('total_revenue', 0),
                    "total_costs": context.summary_stats.get('total_costs', 0),
                    "profit_margin": context.summary_stats.get('profit_margin', 0),
                    "invoice_count": len(context.invoices)
                },
                "resources": {
                    "staff_count": context.summary_stats.get('staff_count', 0),
                    "total_hours": context.summary_stats.get('total_hours', 0),
                    "billable_hours": context.summary_stats.get('billable_hours', 0),
                    "utilization_rate": context.summary_stats.get('utilization_rate', 0)
                },
                "licenses": {
                    "total_licenses": len(context.licenses),
                    "total_cost": context.summary_stats.get('license_cost', 0),
                    "average_utilization": context.summary_stats.get('avg_license_util', 0),
                    "underutilized_count": context.summary_stats.get('underutilized_licenses', 0)
                }
            }
            
            return json.dumps(summary, indent=2)
            
        except Exception as e:
            logger.error(f"Error preparing data context: {e}")
            return json.dumps({"error": "Data context preparation failed"})
    
    def _classify_query_type(self, query: str) -> str:
        """Classify query type for optimal template selection"""
        query_lower = query.lower()
        
        profitability_keywords = ['profit', 'revenue', 'cost', 'margin', 'financial', 'money', 'profitable']
        license_keywords = ['license', 'software', 'utilization', 'waste', 'efficiency', 'subscription']
        resource_keywords = ['staff', 'resource', 'team', 'hours', 'productivity', 'capacity', 'utilization']
        
        if any(keyword in query_lower for keyword in profitability_keywords):
            return "profitability"
        elif any(keyword in query_lower for keyword in license_keywords):
            return "license_efficiency"
        elif any(keyword in query_lower for keyword in resource_keywords):
            return "resource_utilization"
        else:
            return "general_analytics"
    
    async def process_query(self, query: str, context: AnalyticsContext, urgency: str = "normal") -> QueryResult:
        """Process natural language analytics query"""
        start_time = time.time()
        
        try:
            # Determine optimal model
            query_type = self._classify_query_type(query)
            model_name = await self.memory_manager.get_optimal_model("analytics", urgency)
            
            # Load optimal model based on hardware (tinyllama-first approach)
            success = await self.memory_manager.smart_model_load(model_name)
            
            if not success:
                # Hardware-aware fallback: always try tinyllama as final option
                logger.warning(f"Failed to load {model_name}, falling back to tinyllama")
                model_name = "tinyllama"
                success = await self.memory_manager.smart_model_load(model_name)
                
                if not success:
                    raise Exception("Failed to load tinyllama - check Ollama service")
            
            # Prepare context and prompt
            data_context = self._prepare_data_context(context)
            template = self.query_templates[query_type]
            prompt = template.format(data_context=data_context, query=query)
            
            # Process with AI model
            logger.info(f"Processing query with {model_name}: '{query[:50]}...'")
            
            response = await self.memory_manager.ollama.chat(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are MoatMetrics AI, an expert MSP analytics assistant. Provide accurate, actionable insights based on the provided data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            ai_response = response.get('message', {}).get('content', '')
            
            # Extract insights and recommendations
            result = self._parse_ai_response(ai_response, query, query_type)
            result.processing_time = time.time() - start_time
            
            logger.success(f"Query processed in {result.processing_time:.2f}s with confidence {result.confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            # Return fallback response
            return QueryResult(
                answer=f"I apologize, but I encountered an error processing your query: {str(e)}",
                confidence=0.1,
                insights=["System error occurred"],
                recommendations=["Please try again or contact support"],
                data_sources=[],
                processing_time=time.time() - start_time
            )
    
    def _parse_ai_response(self, ai_response: str, original_query: str, query_type: str) -> QueryResult:
        """Parse AI response into structured result"""
        try:
            # Extract answer (first paragraph)
            lines = ai_response.split('\n')
            non_empty_lines = [line.strip() for line in lines if line.strip()]
            
            answer = non_empty_lines[0] if non_empty_lines else "No response generated"
            
            # Extract insights (look for numbered or bulleted lists)
            insights = []
            recommendations = []
            confidence = 0.7  # Default confidence
            
            for line in non_empty_lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['insight', 'trend', 'pattern']):
                    insights.append(line.strip('- •123456789. '))
                elif any(keyword in line_lower for keyword in ['recommend', 'suggest', 'should']):
                    recommendations.append(line.strip('- •123456789. '))
                elif 'confidence' in line_lower and any(c.isdigit() for c in line):
                    # Extract confidence score
                    try:
                        import re
                        numbers = re.findall(r'\d+\.?\d*', line)
                        if numbers:
                            conf_val = float(numbers[0])
                            confidence = conf_val if conf_val <= 1.0 else conf_val / 100.0
                    except:
                        pass
            
            # Ensure we have at least some insights
            if not insights:
                insights = ["Analysis completed based on available data"]
            
            if not recommendations:
                recommendations = ["Continue monitoring metrics for trends"]
            
            return QueryResult(
                answer=answer,
                confidence=confidence,
                insights=insights[:5],  # Limit to top 5
                recommendations=recommendations[:3],  # Limit to top 3
                data_sources=[query_type, "msp_analytics_data"],
                processing_time=0  # Will be set by caller
            )
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return QueryResult(
                answer=ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                confidence=0.5,
                insights=["Response parsing completed with limitations"],
                recommendations=["Review raw response for additional details"],
                data_sources=[query_type],
                processing_time=0
            )
    
    async def batch_process_queries(self, queries: List[str], context: AnalyticsContext) -> List[QueryResult]:
        """Process multiple queries efficiently"""
        logger.info(f"Batch processing {len(queries)} queries")
        
        # Process queries with controlled concurrency
        semaphore = asyncio.Semaphore(2)  # Max 2 concurrent queries
        
        async def process_single(query: str) -> QueryResult:
            async with semaphore:
                return await self.process_query(query, context, urgency="normal")
        
        results = await asyncio.gather(
            *[process_single(query) for query in queries],
            return_exceptions=True
        )
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Query {i} failed: {result}")
                processed_results.append(QueryResult(
                    answer=f"Query failed: {str(result)}",
                    confidence=0.0,
                    insights=[],
                    recommendations=[],
                    data_sources=[],
                    processing_time=0
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system and model configuration"""
        hardware_info = self.memory_manager.get_hardware_info()
        memory_stats = self.memory_manager.get_memory_stats()
        
        return {
            "primary_model": "tinyllama",
            "hardware_tier": hardware_info['tier'],
            "available_models": list(self.memory_manager.model_specs.keys()),
            "current_memory_usage": f"{memory_stats['ai_used_memory_gb']:.1f}GB",
            "available_memory": f"{memory_stats['ai_available_memory_gb']:.1f}GB",
            "cpu_cores": hardware_info['cpu_count'],
            "gpu_available": hardware_info['has_gpu'],
            "platform": hardware_info['platform']
        }
    
    def create_sample_context(self) -> AnalyticsContext:
        """Create sample context for testing"""
        return AnalyticsContext(
            clients=[
                {"id": 1, "name": "TechCorp Solutions", "industry": "Technology", "revenue": 50000},
                {"id": 2, "name": "MedHealth Systems", "industry": "Healthcare", "revenue": 75000},
                {"id": 3, "name": "Finance Plus", "industry": "Finance", "revenue": 35000}
            ],
            invoices=[
                {"client_id": 1, "amount": 15000, "date": "2024-03-01"},
                {"client_id": 2, "amount": 22000, "date": "2024-03-01"},
                {"client_id": 3, "amount": 8000, "date": "2024-03-01"}
            ],
            time_logs=[
                {"staff": "John Doe", "hours": 40, "billable": True, "rate": 125},
                {"staff": "Jane Smith", "hours": 38, "billable": True, "rate": 150}
            ],
            licenses=[
                {"product": "Office 365", "seats_purchased": 25, "seats_used": 18, "cost": 300},
                {"product": "Salesforce", "seats_purchased": 10, "seats_used": 7, "cost": 500}
            ],
            summary_stats={
                "total_revenue": 160000,
                "total_costs": 120000,
                "profit_margin": 0.25,
                "staff_count": 2,
                "total_hours": 78,
                "billable_hours": 78,
                "utilization_rate": 0.95,
                "license_cost": 800,
                "avg_license_util": 0.71,
                "underutilized_licenses": 2
            }
        )
