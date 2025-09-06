"""
Enhanced Natural Language Analytics with Advanced ML Optimization and Security
Integrates cutting-edge ML algorithms, security frameworks, and optimization techniques
"""
import asyncio
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from loguru import logger

# Import base components
from .nl_analytics import NaturalLanguageAnalytics, AnalyticsContext, QueryResult
from .memory_manager import AIMemoryManager
from .advanced_ml_optimizer import AdvancedMLOptimizer
from .advanced_security import AdvancedSecurityFramework


@dataclass
class EnhancedQueryResult:
    """Enhanced query result with advanced ML and security metrics"""
    answer: str
    confidence: float
    insights: List[str]
    recommendations: List[str]
    data_sources: List[str]
    processing_time: float
    
    # Enhanced fields
    optimization_applied: str
    cache_hit: bool
    security_score: float
    privacy_level: str
    model_used: str
    quality_score: float
    uncertainty_bounds: Tuple[float, float]
    ensemble_agreement: float


class EnhancedNaturalLanguageAnalytics:
    """Enhanced NL Analytics with advanced ML optimization and security"""
    
    def __init__(self, memory_manager: AIMemoryManager):
        self.memory_manager = memory_manager
        self.base_analytics = NaturalLanguageAnalytics(memory_manager)
        self.ml_optimizer = AdvancedMLOptimizer(cache_size=2000)
        self.security_framework = AdvancedSecurityFramework()
        
        # Enhanced features
        self.ensemble_models = ['tinyllama', 'phi3:mini']  # Available for ensemble
        self.quality_threshold = 0.6
        self.uncertainty_estimation = True
        self.adaptive_confidence = True
        
        logger.info("Enhanced Natural Language Analytics initialized")
    
    async def initialize(self):
        """Initialize all enhanced components"""
        logger.info("Initializing Enhanced NL Analytics components...")
        
        await self.ml_optimizer.initialize()
        await self.security_framework.initialize()
        
        logger.success("Enhanced NL Analytics fully initialized")
    
    async def process_query_enhanced(self, query: str, context: AnalyticsContext,
                                   urgency: str = "normal", 
                                   privacy_level: str = "standard",
                                   enable_ensemble: bool = False) -> EnhancedQueryResult:
        """Process query with advanced ML optimization and security"""
        start_time = time.time()
        
        try:
            # 1. Security preprocessing
            context_hash = self._generate_context_hash(context)
            
            security_result = await self.security_framework.secure_query_processing(
                query, {'urgency': urgency}
            )
            
            if security_result['status'] == 'BLOCKED':
                return self._create_blocked_response(security_result, start_time)
            
            # 2. ML optimization preprocessing
            model_complexity = self._estimate_query_complexity(query)
            optimization_result = await self.ml_optimizer.optimize_query(
                query, context_hash, model_complexity
            )
            
            # 3. Check for cached response
            if optimization_result.get('cache_hit'):
                cached_response = optimization_result['response']
                return self._enhance_cached_response(cached_response, security_result, start_time)
            
            # 4. Process with appropriate model(s)
            if enable_ensemble and len(self.ensemble_models) > 1:
                query_result = await self._process_with_ensemble(
                    query, context, urgency, optimization_result
                )
            else:
                query_result = await self._process_with_single_model(
                    query, context, urgency, optimization_result
                )
            
            # 5. Apply post-processing optimizations
            optimized_result = await self.ml_optimizer.postprocess_response(
                query_result.__dict__, query, context_hash
            )
            
            # 6. Apply privacy protection
            privacy_protected = await self.security_framework.apply_privacy_protection(
                optimized_result, privacy_level
            )
            
            # 7. Enhance with advanced metrics
            enhanced_result = self._create_enhanced_result(
                query_result, privacy_protected, security_result, 
                optimization_result, start_time
            )
            
            # 8. Quality assessment and uncertainty quantification
            if self.uncertainty_estimation:
                enhanced_result = await self._add_uncertainty_quantification(enhanced_result, query, context)
            
            logger.success(f"Enhanced query processed in {enhanced_result.processing_time:.2f}s "
                          f"(Security: {enhanced_result.security_score:.2f}, "
                          f"Quality: {enhanced_result.quality_score:.2f})")
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Enhanced query processing failed: {e}")
            return self._create_error_response(str(e), start_time)
    
    async def _process_with_ensemble(self, query: str, context: AnalyticsContext,
                                   urgency: str, optimization_result: Dict[str, Any]) -> QueryResult:
        """Process query using ensemble of models for better accuracy"""
        logger.info(f"Processing with ensemble of {len(self.ensemble_models)} models")
        
        # Get results from multiple models
        ensemble_results = []
        
        for model_name in self.ensemble_models:
            try:
                # Load specific model
                success = await self.memory_manager.smart_model_load(model_name)
                if not success:
                    continue
                
                # Process query with this model
                model_result = await self.base_analytics.process_query(
                    query, context, urgency
                )
                
                ensemble_results.append({
                    'model': model_name,
                    'result': model_result,
                    'confidence': model_result.confidence
                })
                
            except Exception as e:
                logger.warning(f"Ensemble model {model_name} failed: {e}")
                continue
        
        if not ensemble_results:
            # Fallback to single model
            return await self.base_analytics.process_query(query, context, urgency)
        
        # Ensemble aggregation
        return self._aggregate_ensemble_results(ensemble_results)
    
    async def _process_with_single_model(self, query: str, context: AnalyticsContext,
                                       urgency: str, optimization_result: Dict[str, Any]) -> QueryResult:
        """Process query with single optimized model"""
        return await self.base_analytics.process_query(query, context, urgency)
    
    def _aggregate_ensemble_results(self, ensemble_results: List[Dict[str, Any]]) -> QueryResult:
        """Aggregate results from ensemble of models"""
        if not ensemble_results:
            return self._create_empty_result()
        
        if len(ensemble_results) == 1:
            return ensemble_results[0]['result']
        
        # Weighted voting by confidence
        total_confidence = sum(r['confidence'] for r in ensemble_results)
        weights = [r['confidence'] / total_confidence for r in ensemble_results]
        
        # Aggregate answers (choose highest confidence)
        best_result = max(ensemble_results, key=lambda x: x['confidence'])
        
        # Aggregate insights and recommendations
        all_insights = []
        all_recommendations = []
        
        for result_data in ensemble_results:
            result = result_data['result']
            all_insights.extend(result.insights)
            all_recommendations.extend(result.recommendations)
        
        # Remove duplicates and select top items
        unique_insights = list(dict.fromkeys(all_insights))[:5]
        unique_recommendations = list(dict.fromkeys(all_recommendations))[:3]
        
        # Calculate ensemble confidence
        ensemble_confidence = np.mean([r['confidence'] for r in ensemble_results])
        
        # Calculate processing time
        max_processing_time = max(r['result'].processing_time for r in ensemble_results)
        
        return QueryResult(
            answer=best_result['result'].answer,
            confidence=ensemble_confidence,
            insights=unique_insights,
            recommendations=unique_recommendations,
            data_sources=list(set(sum([r['result'].data_sources for r in ensemble_results], []))),
            processing_time=max_processing_time
        )
    
    async def _add_uncertainty_quantification(self, result: EnhancedQueryResult, 
                                            query: str, context: AnalyticsContext) -> EnhancedQueryResult:
        """Add uncertainty bounds and quality metrics"""
        # Simple uncertainty estimation based on confidence variance
        base_uncertainty = 1.0 - result.confidence
        
        # Factor in query complexity
        query_complexity = self._estimate_query_complexity(query)
        complexity_uncertainty = query_complexity * 0.2
        
        # Factor in data quality
        data_quality = self._assess_data_quality(context)
        data_uncertainty = (1.0 - data_quality) * 0.3
        
        # Total uncertainty
        total_uncertainty = min(0.5, base_uncertainty + complexity_uncertainty + data_uncertainty)
        
        # Confidence bounds
        lower_bound = max(0.0, result.confidence - total_uncertainty)
        upper_bound = min(1.0, result.confidence + total_uncertainty)
        
        result.uncertainty_bounds = (lower_bound, upper_bound)
        
        # Quality score based on various factors
        quality_factors = [
            result.confidence,
            1.0 - total_uncertainty,
            result.security_score,
            data_quality,
            min(1.0, result.ensemble_agreement)  # Agreement between models
        ]
        
        result.quality_score = np.mean(quality_factors)
        
        return result
    
    def _estimate_query_complexity(self, query: str) -> float:
        """Estimate query complexity for optimization decisions"""
        # Simple heuristic-based complexity estimation
        complexity_score = 0.0
        
        # Length factor
        complexity_score += min(0.3, len(query) / 500)
        
        # Keyword complexity
        complex_keywords = ['analyze', 'compare', 'correlate', 'predict', 'optimize', 'summarize']
        complexity_score += sum(0.1 for kw in complex_keywords if kw.lower() in query.lower())
        
        # Question type complexity
        if '?' in query:
            question_words = ['why', 'how', 'what if', 'compare', 'analyze']
            complexity_score += sum(0.1 for qw in question_words if qw.lower() in query.lower())
        
        return min(1.0, complexity_score)
    
    def _assess_data_quality(self, context: AnalyticsContext) -> float:
        """Assess quality of input data"""
        quality_score = 1.0
        
        # Check data completeness
        if not context.clients:
            quality_score -= 0.2
        if not context.invoices:
            quality_score -= 0.2
        if not context.time_logs:
            quality_score -= 0.2
        if not context.licenses:
            quality_score -= 0.2
        
        # Check data consistency
        if context.summary_stats:
            expected_revenue = sum(invoice.get('amount', 0) for invoice in context.invoices)
            reported_revenue = context.summary_stats.get('total_revenue', 0)
            
            if expected_revenue > 0 and reported_revenue > 0:
                revenue_ratio = min(expected_revenue, reported_revenue) / max(expected_revenue, reported_revenue)
                if revenue_ratio < 0.8:
                    quality_score -= 0.2
        
        return max(0.0, quality_score)
    
    def _generate_context_hash(self, context: AnalyticsContext) -> str:
        """Generate hash for caching context"""
        context_str = json.dumps({
            'clients_count': len(context.clients),
            'invoices_count': len(context.invoices),
            'summary_key': str(sorted(context.summary_stats.keys())) if context.summary_stats else "",
        }, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()
    
    def _create_enhanced_result(self, base_result: QueryResult, 
                              privacy_result: Dict[str, Any],
                              security_result: Dict[str, Any],
                              optimization_result: Dict[str, Any],
                              start_time: float) -> EnhancedQueryResult:
        """Create enhanced result from base components"""
        
        return EnhancedQueryResult(
            answer=base_result.answer,
            confidence=privacy_result.get('confidence', base_result.confidence),
            insights=base_result.insights,
            recommendations=base_result.recommendations,
            data_sources=base_result.data_sources,
            processing_time=time.time() - start_time,
            
            # Enhanced fields
            optimization_applied=optimization_result.get('optimization_path', {}).get('optimization', 'none'),
            cache_hit=optimization_result.get('cache_hit', False),
            security_score=security_result['security_results']['security_score'],
            privacy_level=privacy_result.get('privacy_level', 'standard'),
            model_used='tinyllama',  # Primary model
            quality_score=0.8,  # Will be updated by uncertainty quantification
            uncertainty_bounds=(0.0, 1.0),  # Will be updated by uncertainty quantification
            ensemble_agreement=1.0  # Single model = perfect agreement
        )
    
    def _enhance_cached_response(self, cached_response: Dict[str, Any],
                               security_result: Dict[str, Any], 
                               start_time: float) -> EnhancedQueryResult:
        """Enhance cached response with current security and optimization data"""
        return EnhancedQueryResult(
            answer=cached_response.get('answer', ''),
            confidence=cached_response.get('confidence', 0.5),
            insights=cached_response.get('insights', []),
            recommendations=cached_response.get('recommendations', []),
            data_sources=cached_response.get('data_sources', []),
            processing_time=time.time() - start_time,
            
            optimization_applied='semantic_cache_hit',
            cache_hit=True,
            security_score=security_result['security_results']['security_score'],
            privacy_level='standard',
            model_used='cached',
            quality_score=cached_response.get('quality_score', 0.7),
            uncertainty_bounds=(0.0, 1.0),
            ensemble_agreement=1.0
        )
    
    def _create_blocked_response(self, security_result: Dict[str, Any], 
                               start_time: float) -> EnhancedQueryResult:
        """Create response for blocked queries"""
        return EnhancedQueryResult(
            answer="Query blocked due to security concerns.",
            confidence=1.0,
            insights=["Security threat detected"],
            recommendations=["Review query content for potential security issues"],
            data_sources=["security_system"],
            processing_time=time.time() - start_time,
            
            optimization_applied='security_block',
            cache_hit=False,
            security_score=0.0,
            privacy_level='high',
            model_used='security_filter',
            quality_score=1.0,  # High quality block
            uncertainty_bounds=(1.0, 1.0),
            ensemble_agreement=1.0
        )
    
    def _create_error_response(self, error_message: str, start_time: float) -> EnhancedQueryResult:
        """Create response for error conditions"""
        return EnhancedQueryResult(
            answer=f"An error occurred during processing: {error_message}",
            confidence=0.0,
            insights=["System error occurred"],
            recommendations=["Please try again or contact support"],
            data_sources=["error_system"],
            processing_time=time.time() - start_time,
            
            optimization_applied='error_fallback',
            cache_hit=False,
            security_score=0.5,
            privacy_level='standard',
            model_used='error_handler',
            quality_score=0.0,
            uncertainty_bounds=(0.0, 0.0),
            ensemble_agreement=0.0
        )
    
    def _create_empty_result(self) -> QueryResult:
        """Create empty result for fallback"""
        return QueryResult(
            answer="Unable to process query.",
            confidence=0.0,
            insights=[],
            recommendations=[],
            data_sources=[],
            processing_time=0.0
        )
    
    async def batch_process_enhanced(self, queries: List[str], context: AnalyticsContext,
                                   privacy_level: str = "standard",
                                   enable_ensemble: bool = False) -> List[EnhancedQueryResult]:
        """Process multiple queries with advanced optimization"""
        logger.info(f"Enhanced batch processing {len(queries)} queries")
        
        # Control concurrency based on system resources
        max_concurrent = min(3, len(queries))  # Limit concurrent processing
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single_enhanced(query: str) -> EnhancedQueryResult:
            async with semaphore:
                return await self.process_query_enhanced(
                    query, context, urgency="normal", 
                    privacy_level=privacy_level,
                    enable_ensemble=enable_ensemble
                )
        
        results = await asyncio.gather(
            *[process_single_enhanced(query) for query in queries],
            return_exceptions=True
        )
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Enhanced query {i} failed: {result}")
                error_result = self._create_error_response(str(result), 0.0)
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def get_comprehensive_analytics_report(self) -> Dict[str, Any]:
        """Get comprehensive report including all optimization and security metrics"""
        
        # Get base analytics info
        system_info = self.base_analytics.get_system_info()
        
        # Get optimization metrics
        optimization_report = await self.ml_optimizer.get_system_performance_report()
        
        # Get security metrics
        security_report = await self.security_framework.get_comprehensive_security_report()
        
        return {
            "system_configuration": system_info,
            "ml_optimization": optimization_report,
            "security_framework": security_report,
            "enhanced_features": {
                "ensemble_models_available": len(self.ensemble_models),
                "uncertainty_estimation": self.uncertainty_estimation,
                "adaptive_confidence": self.adaptive_confidence,
                "quality_threshold": self.quality_threshold
            },
            "integration_status": "fully_operational",
            "timestamp": time.time()
        }
    
    async def cleanup(self):
        """Cleanup all enhanced components"""
        logger.info("Cleaning up Enhanced Natural Language Analytics...")
        
        await self.ml_optimizer.cleanup()
        await self.security_framework.cleanup()
        
        logger.success("Enhanced Natural Language Analytics cleanup completed")
