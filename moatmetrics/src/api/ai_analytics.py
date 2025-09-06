"""
AI Analytics API Endpoints
Provides natural language analytics capabilities and AI system management
"""
import asyncio
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from loguru import logger

from ..ai.memory_manager import AIMemoryManager
from ..ai.nl_analytics import NaturalLanguageAnalytics, AnalyticsContext, QueryResult
from ..ai.enhanced_nl_analytics import EnhancedNaturalLanguageAnalytics, EnhancedQueryResult
from ..utils.config_loader import get_config
from ..utils.database import get_db_manager
from .auth import get_current_user, require_role

router = APIRouter(prefix="/api/ai", tags=["AI Analytics"])

# Global AI components - initialized on startup
memory_manager: Optional[AIMemoryManager] = None
nl_analytics: Optional[NaturalLanguageAnalytics] = None
enhanced_analytics: Optional[EnhancedNaturalLanguageAnalytics] = None

# Request/Response Models
class AIQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    urgency: str = Field(default="normal", description="Query urgency: low, normal, high")
    enhanced: bool = Field(default=False, description="Use enhanced AI with ML optimization")
    privacy_level: str = Field(default="standard", description="Privacy level: low, standard, high")
    enable_ensemble: bool = Field(default=False, description="Use ensemble of models for better accuracy")

class AIQueryResponse(BaseModel):
    success: bool
    answer: str
    confidence: float
    insights: List[str]
    recommendations: List[str]
    processing_time: float
    model_used: str
    data_sources: List[str]
    
    # Enhanced fields (optional)
    optimization_applied: Optional[str] = None
    cache_hit: Optional[bool] = None
    security_score: Optional[float] = None
    privacy_level: Optional[str] = None
    quality_score: Optional[float] = None
    uncertainty_bounds: Optional[List[float]] = None
    ensemble_agreement: Optional[float] = None

class AISystemInfoResponse(BaseModel):
    status: str
    primary_model: str
    hardware_tier: str
    available_models: List[str]
    current_memory_usage: str
    available_memory: str
    cpu_cores: int
    gpu_available: bool
    platform: str
    ollama_status: str
    enhanced_features_available: bool

class AIBatchQueryRequest(BaseModel):
    queries: List[str] = Field(..., description="List of natural language queries")
    enhanced: bool = Field(default=False, description="Use enhanced AI features")
    privacy_level: str = Field(default="standard", description="Privacy level for all queries")
    enable_ensemble: bool = Field(default=False, description="Use ensemble processing")

def get_memory_manager() -> Optional[AIMemoryManager]:
    """Get the global memory manager instance"""
    return memory_manager

# Startup function to initialize AI components
async def initialize_ai_components():
    """Initialize AI components during application startup"""
    global memory_manager, nl_analytics, enhanced_analytics
    
    try:
        logger.info("Initializing AI Analytics components...")
        
        # Check if Ollama is running
        try:
            from ..ai.memory_manager import OllamaClient
            client = OllamaClient()
            await client._ensure_session()
            async with client.session.get(f"{client.base_url}/api/tags") as resp:
                if resp.status != 200:
                    raise Exception(f"Ollama API returned status {resp.status}")
                models = await resp.json()
                logger.info(f"Connected to Ollama. Available models: {[m['name'] for m in models.get('models', [])] if 'models' in models else 'unknown'}")
        except Exception as e:
            logger.warning(f"Ollama connection check failed: {e}")
            logger.warning("AI features will be limited. Make sure Ollama is running for full functionality.")
            # Continue initialization even if Ollama check fails
            pass
        
        # Initialize memory manager
        memory_manager = AIMemoryManager()
        await memory_manager.initialize()
        
        # Initialize natural language analytics
        nl_analytics = NaturalLanguageAnalytics(memory_manager)
        
        # Initialize enhanced analytics
        enhanced_analytics = EnhancedNaturalLanguageAnalytics(memory_manager)
        await enhanced_analytics.initialize()
        
        # Ensure approved model is loaded
        approved_model = 'tinyllama'
        model_loaded = await memory_manager.smart_model_load(approved_model)
        if not model_loaded:
            logger.warning(f"Failed to load approved model: {approved_model}")
            return False
            
        logger.success("AI Analytics components initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize AI components: {e}")
        return False

# Dependency to ensure AI is initialized
async def get_ai_components():
    """Dependency to get initialized AI components"""
    if not all([memory_manager, nl_analytics, enhanced_analytics]):
        raise HTTPException(
            status_code=503, 
            detail="AI Analytics components are not initialized. Please check system status."
        )
    return {
        "memory_manager": memory_manager,
        "nl_analytics": nl_analytics,
        "enhanced_analytics": enhanced_analytics
    }

async def get_analytics_context() -> AnalyticsContext:
    """Get current analytics context from database"""
    try:
        db_manager = get_db_manager()
        
        # Get data from database
        clients = await db_manager.get_all_clients() or []
        invoices = await db_manager.get_all_invoices() or []
        time_logs = await db_manager.get_all_time_logs() or []
        licenses = await db_manager.get_all_licenses() or []
        
        # Calculate summary statistics
        total_revenue = sum(invoice.get('amount', 0) for invoice in invoices)
        total_costs = sum(invoice.get('cost', 0) for invoice in invoices)
        profit_margin = (total_revenue - total_costs) / total_revenue if total_revenue > 0 else 0
        
        total_hours = sum(log.get('hours', 0) for log in time_logs)
        billable_hours = sum(log.get('hours', 0) for log in time_logs if log.get('billable', False))
        utilization_rate = billable_hours / total_hours if total_hours > 0 else 0
        
        license_cost = sum(license.get('cost', 0) for license in licenses)
        avg_utilization = sum(
            license.get('seats_used', 0) / max(license.get('seats_purchased', 1), 1)
            for license in licenses
        ) / len(licenses) if licenses else 0
        
        underutilized_licenses = sum(
            1 for license in licenses
            if (license.get('seats_used', 0) / max(license.get('seats_purchased', 1), 1)) < 0.7
        )
        
        summary_stats = {
            "total_revenue": total_revenue,
            "total_costs": total_costs,
            "profit_margin": profit_margin,
            "staff_count": len(set(log.get('staff_name', '') for log in time_logs)),
            "total_hours": total_hours,
            "billable_hours": billable_hours,
            "utilization_rate": utilization_rate,
            "license_cost": license_cost,
            "avg_license_util": avg_utilization,
            "underutilized_licenses": underutilized_licenses
        }
        
        return AnalyticsContext(
            clients=clients,
            invoices=invoices,
            time_logs=time_logs,
            licenses=licenses,
            summary_stats=summary_stats
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics context: {e}")
        # Return sample context if database unavailable
        return nl_analytics.create_sample_context() if nl_analytics else AnalyticsContext(
            clients=[], invoices=[], time_logs=[], licenses=[], summary_stats={}
        )

@router.get("/status", response_model=AISystemInfoResponse)
async def get_ai_status(ai_components = Depends(get_ai_components)):
    """Get AI system status and configuration"""
    try:
        memory_mgr = ai_components["memory_manager"]
        nl_analytics_svc = ai_components["nl_analytics"]
        
        system_info = nl_analytics_svc.get_system_info()
        
        # Check Ollama status
        ollama_status = "available" if await memory_mgr.check_ollama_status() else "unavailable"
        
        return AISystemInfoResponse(
            status="operational",
            primary_model=system_info["primary_model"],
            hardware_tier=system_info["hardware_tier"],
            available_models=system_info["available_models"],
            current_memory_usage=system_info["current_memory_usage"],
            available_memory=system_info["available_memory"],
            cpu_cores=system_info["cpu_cores"],
            gpu_available=system_info["gpu_available"],
            platform=system_info["platform"],
            ollama_status=ollama_status,
            enhanced_features_available=True
        )
        
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI status: {str(e)}")

@router.post("/query", response_model=AIQueryResponse)
async def process_ai_query(
    request: AIQueryRequest,
    current_user: dict = Depends(get_current_user),
    ai_components = Depends(get_ai_components)
):
    """Process natural language analytics query"""
    try:
        # Get analytics context
        context = await get_analytics_context()
        
        # Choose processing method
        if request.enhanced:
            enhanced_analytics_svc = ai_components["enhanced_analytics"]
            result = await enhanced_analytics_svc.process_query_enhanced(
                query=request.query,
                context=context,
                urgency=request.urgency,
                privacy_level=request.privacy_level,
                enable_ensemble=request.enable_ensemble
            )
            
            # Convert enhanced result to response format
            return AIQueryResponse(
                success=True,
                answer=result.answer,
                confidence=result.confidence,
                insights=result.insights,
                recommendations=result.recommendations,
                processing_time=result.processing_time,
                model_used=result.model_used,
                data_sources=result.data_sources,
                optimization_applied=result.optimization_applied,
                cache_hit=result.cache_hit,
                security_score=result.security_score,
                privacy_level=result.privacy_level,
                quality_score=result.quality_score,
                uncertainty_bounds=list(result.uncertainty_bounds),
                ensemble_agreement=result.ensemble_agreement
            )
            
        else:
            nl_analytics_svc = ai_components["nl_analytics"]
            result = await nl_analytics_svc.process_query(
                query=request.query,
                context=context,
                urgency=request.urgency
            )
            
            return AIQueryResponse(
                success=True,
                answer=result.answer,
                confidence=result.confidence,
                insights=result.insights,
                recommendations=result.recommendations,
                processing_time=result.processing_time,
                model_used="tinyllama",  # Primary model
                data_sources=result.data_sources
            )
            
    except Exception as e:
        logger.error(f"Error processing AI query: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

@router.post("/batch-query")
async def process_batch_queries(
    request: AIBatchQueryRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    ai_components = Depends(get_ai_components)
):
    """Process multiple natural language queries in batch"""
    try:
        if len(request.queries) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 queries allowed per batch")
        
        # Get analytics context
        context = await get_analytics_context()
        
        # Process queries
        if request.enhanced:
            enhanced_analytics_svc = ai_components["enhanced_analytics"]
            results = await enhanced_analytics_svc.batch_process_enhanced(
                queries=request.queries,
                context=context,
                privacy_level=request.privacy_level,
                enable_ensemble=request.enable_ensemble
            )
            
            # Convert results
            response_results = []
            for result in results:
                response_results.append({
                    "answer": result.answer,
                    "confidence": result.confidence,
                    "insights": result.insights,
                    "recommendations": result.recommendations,
                    "processing_time": result.processing_time,
                    "model_used": result.model_used,
                    "optimization_applied": result.optimization_applied,
                    "cache_hit": result.cache_hit,
                    "security_score": result.security_score,
                    "quality_score": result.quality_score
                })
                
        else:
            nl_analytics_svc = ai_components["nl_analytics"]
            results = await nl_analytics_svc.batch_process_queries(
                queries=request.queries,
                context=context
            )
            
            response_results = []
            for result in results:
                response_results.append({
                    "answer": result.answer,
                    "confidence": result.confidence,
                    "insights": result.insights,
                    "recommendations": result.recommendations,
                    "processing_time": result.processing_time,
                    "model_used": "tinyllama",
                    "data_sources": result.data_sources
                })
        
        return {
            "success": True,
            "total_queries": len(request.queries),
            "results": response_results,
            "total_processing_time": sum(r["processing_time"] for r in response_results)
        }
        
    except Exception as e:
        logger.error(f"Error processing batch queries: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process batch queries: {str(e)}")

@router.get("/models")
async def get_available_models(
    current_user: dict = Depends(require_role("admin")),
    ai_components = Depends(get_ai_components)
):
    """Get list of available AI models (Admin only)"""
    try:
        memory_mgr = ai_components["memory_manager"]
        
        models_info = []
        for model_name, model_info in memory_mgr.model_specs.items():
            models_info.append({
                "name": model_name,
                "memory_required_gb": model_info.size_gb if hasattr(model_info, 'size_gb') else 0,
                "parameters": getattr(model_info, 'parameters', 'unknown'),
                "description": getattr(model_info, 'description', 'AI Language Model'),
                "status": "available" if await memory_mgr.check_model_availability(model_name) else "unavailable",
                "last_used": getattr(model_info, 'last_used', 0),
                "status": getattr(model_info, 'status', 'unknown')
            })
        
        return {
            "success": True,
            "models": models_info,
            "total_models": len(models_info),
            "hardware_tier": memory_mgr.get_hardware_info()["tier"]
        }
        
    except Exception as e:
        logger.error(f"Error getting models info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get models info: {str(e)}")

@router.post("/models/{model_name}/load")
async def load_model(
    model_name: str,
    current_user: dict = Depends(require_role("admin")),
    ai_components = Depends(get_ai_components)
):
    """Load specific AI model (Admin only)"""
    try:
        memory_mgr = ai_components["memory_manager"]
        
        success = await memory_mgr.smart_model_load(model_name)
        
        if success:
            return {
                "success": True,
                "message": f"Model {model_name} loaded successfully",
                "model_name": model_name
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to load model {model_name}. Check availability and system resources."
            )
            
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

@router.get("/performance-report")
async def get_performance_report(
    current_user: dict = Depends(require_role("admin")),
    ai_components = Depends(get_ai_components)
):
    """Get comprehensive AI performance report (Admin only)"""
    try:
        enhanced_analytics_svc = ai_components["enhanced_analytics"]
        
        report = await enhanced_analytics_svc.get_comprehensive_analytics_report()
        
        return {
            "success": True,
            "report": report,
            "timestamp": report.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Error getting performance report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance report: {str(e)}")

@router.post("/initialize")
async def initialize_ai_system(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role("admin"))
):
    """Initialize or reinitialize AI system (Admin only)"""
    
    async def init_task():
        success = await initialize_ai_components()
        logger.info(f"AI system initialization {'successful' if success else 'failed'}")
    
    background_tasks.add_task(init_task)
    
    return {
        "success": True,
        "message": "AI system initialization started in background",
        "status": "initializing"
    }

# Health check endpoint
@router.get("/health")
async def ai_health_check():
    """Check AI system health"""
    try:
        if not all([memory_manager, nl_analytics, enhanced_analytics]):
            return {
                "status": "not_initialized",
                "message": "AI components not initialized",
                "services": {
                    "memory_manager": memory_manager is not None,
                    "nl_analytics": nl_analytics is not None,
                    "enhanced_analytics": enhanced_analytics is not None
                }
            }
        
        # Check Ollama status
        ollama_status = await memory_manager.check_ollama_status()
        
        # Convert objects to dict for proper serialization
        memory_stats = memory_manager.get_memory_stats()
        if hasattr(memory_stats, 'dict'):
            memory_stats = memory_stats.dict()
            
        hardware_info = memory_manager.get_hardware_info()
        if hasattr(hardware_info, 'dict'):
            hardware_info = hardware_info.dict()
        
        return {
            "status": "healthy" if ollama_status else "degraded",
            "message": "AI system is operational" if ollama_status else "AI system is running with degraded performance",
            "services": {
                "ollama": {
                    "status": "ok" if ollama_status else "unavailable",
                    "models": [m.name for m in memory_manager.loaded_models.values()] if hasattr(memory_manager, 'loaded_models') else []
                },
                "memory_manager": True,
                "nl_analytics": True,
                "enhanced_analytics": True
            },
            "resources": memory_stats,
            "hardware": hardware_info
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "services": {},
            "error": str(e)
        }
