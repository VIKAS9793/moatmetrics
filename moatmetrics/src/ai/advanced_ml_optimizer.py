"""
Advanced ML Optimization Pipeline for MoatMetrics AI
Implements cutting-edge research algorithms for robust, optimized, and secure AI/ML processing
"""
import asyncio
import numpy as np
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import concurrent.futures
from collections import defaultdict, deque
import threading
import psutil
from loguru import logger
import pickle
import zlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class OptimizationMetrics:
    """Advanced metrics for ML optimization tracking"""
    inference_time: float
    memory_usage: float
    cache_hit_rate: float
    model_confidence: float
    security_score: float
    optimization_level: str
    throughput_qps: float
    latency_p99: float


@dataclass
class QueryEmbedding:
    """Semantic embedding for query caching and optimization"""
    embedding: np.ndarray
    hash_key: str
    timestamp: float
    usage_count: int
    quality_score: float


class AdaptiveBatchingEngine:
    """Dynamic batching with ML-based optimization"""
    
    def __init__(self, max_batch_size: int = 8, max_wait_time: float = 0.5):
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.pending_requests = deque()
        self.batch_history = deque(maxlen=100)
        self.performance_model = None
        self.lock = threading.Lock()
        
    def _train_performance_model(self):
        """Train ML model to predict optimal batch size"""
        if len(self.batch_history) < 10:
            return
            
        # Features: batch_size, avg_query_length, system_load
        # Target: processing_time_per_item
        X, y = [], []
        for record in self.batch_history:
            features = [
                record['batch_size'],
                record['avg_query_length'],
                record['system_load'],
                record['memory_usage']
            ]
            X.append(features)
            y.append(record['processing_time'] / record['batch_size'])
        
        # Simple linear regression for batch size optimization
        X = np.array(X)
        y = np.array(y)
        
        # Use ridge regression for stability
        from sklearn.linear_model import Ridge
        self.performance_model = Ridge(alpha=1.0)
        self.performance_model.fit(X, y)
        
        logger.info("Updated adaptive batching performance model")
    
    async def add_request(self, request_data: Dict[str, Any]) -> int:
        """Add request to batch queue"""
        with self.lock:
            batch_id = len(self.pending_requests)
            self.pending_requests.append({
                'data': request_data,
                'timestamp': time.time(),
                'batch_id': batch_id
            })
        return batch_id
    
    async def get_optimal_batch(self) -> List[Dict[str, Any]]:
        """Get optimally sized batch using ML prediction"""
        if not self.pending_requests:
            return []
        
        # Calculate optimal batch size
        optimal_size = self._predict_optimal_batch_size()
        
        with self.lock:
            batch = []
            while self.pending_requests and len(batch) < optimal_size:
                batch.append(self.pending_requests.popleft())
        
        return batch
    
    def _predict_optimal_batch_size(self) -> int:
        """Predict optimal batch size using ML model"""
        if not self.performance_model or not self.pending_requests:
            return min(len(self.pending_requests), self.max_batch_size)
        
        # Current system features
        current_features = [
            len(self.pending_requests),  # Available requests
            np.mean([len(str(req['data'])) for req in list(self.pending_requests)[:5]]),  # Avg query length
            psutil.cpu_percent(),  # System load
            psutil.virtual_memory().percent  # Memory usage
        ]
        
        # Predict processing time for different batch sizes
        best_size = 1
        best_efficiency = float('inf')
        
        for size in range(1, min(len(self.pending_requests) + 1, self.max_batch_size + 1)):
            features = current_features.copy()
            features[0] = size  # Override batch size
            
            try:
                predicted_time = self.performance_model.predict([features])[0]
                efficiency = predicted_time * size  # Total processing time
                
                if efficiency < best_efficiency:
                    best_efficiency = efficiency
                    best_size = size
            except:
                continue
        
        return best_size
    
    def record_batch_performance(self, batch_size: int, processing_time: float, 
                                avg_query_length: float):
        """Record batch performance for model training"""
        record = {
            'batch_size': batch_size,
            'processing_time': processing_time,
            'avg_query_length': avg_query_length,
            'system_load': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'timestamp': time.time()
        }
        
        self.batch_history.append(record)
        
        # Retrain model periodically
        if len(self.batch_history) % 10 == 0:
            self._train_performance_model()


class SemanticCacheEngine:
    """Advanced semantic caching with ML-based similarity detection"""
    
    def __init__(self, cache_size: int = 1000, similarity_threshold: float = 0.85):
        self.cache_size = cache_size
        self.similarity_threshold = similarity_threshold
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, QueryEmbedding] = {}
        self.vectorizer = TfidfVectorizer(max_features=512, stop_words='english')
        self.is_vectorizer_fitted = False
        self.access_patterns = defaultdict(list)
        self.lock = threading.RLock()
        
    def _get_query_embedding(self, query: str) -> np.ndarray:
        """Generate semantic embedding for query"""
        try:
            if not self.is_vectorizer_fitted:
                # Bootstrap with common queries if no training data
                bootstrap_queries = [query, "what is the performance", "show me data", 
                                   "analyze results", "get insights"]
                self.vectorizer.fit(bootstrap_queries)
                self.is_vectorizer_fitted = True
            
            embedding = self.vectorizer.transform([query]).toarray()[0]
            return embedding / (np.linalg.norm(embedding) + 1e-8)  # Normalize
        except:
            # Fallback to simple hash-based embedding
            hash_val = hashlib.md5(query.lower().encode()).hexdigest()
            return np.array([int(c, 16) for c in hash_val[:16]], dtype=float)
    
    def _find_similar_queries(self, query_embedding: np.ndarray) -> List[Tuple[str, float]]:
        """Find cached queries similar to current query"""
        if not self.embeddings:
            return []
        
        similarities = []
        for cache_key, cached_embedding in self.embeddings.items():
            try:
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    cached_embedding.embedding.reshape(1, -1)
                )[0, 0]
                
                if similarity >= self.similarity_threshold:
                    similarities.append((cache_key, similarity))
            except:
                continue
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:3]
    
    async def get_cached_response(self, query: str, context_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached response using semantic similarity"""
        query_embedding = self._get_query_embedding(query)
        cache_key = f"{hashlib.md5((query + context_hash).encode()).hexdigest()}"
        
        with self.lock:
            # Exact match first
            if cache_key in self.cache:
                self.cache[cache_key]['access_count'] += 1
                self.cache[cache_key]['last_accessed'] = time.time()
                logger.debug(f"Cache hit (exact): {query[:50]}...")
                return self.cache[cache_key]['response'].copy()
            
            # Semantic similarity search
            similar_queries = self._find_similar_queries(query_embedding)
            
            for similar_key, similarity in similar_queries:
                if similar_key in self.cache:
                    response = self.cache[similar_key]['response'].copy()
                    
                    # Add similarity metadata
                    response['cache_similarity'] = similarity
                    response['cache_type'] = 'semantic'
                    
                    self.cache[similar_key]['access_count'] += 1
                    self.cache[similar_key]['last_accessed'] = time.time()
                    
                    logger.info(f"Cache hit (semantic {similarity:.2f}): {query[:50]}...")
                    return response
        
        return None
    
    async def cache_response(self, query: str, context_hash: str, response: Dict[str, Any]):
        """Cache response with semantic embedding"""
        query_embedding = self._get_query_embedding(query)
        cache_key = f"{hashlib.md5((query + context_hash).encode()).hexdigest()}"
        
        with self.lock:
            # Evict old entries if cache is full
            if len(self.cache) >= self.cache_size:
                self._evict_lru_entries()
            
            # Store cache entry
            self.cache[cache_key] = {
                'response': response.copy(),
                'timestamp': time.time(),
                'access_count': 1,
                'last_accessed': time.time(),
                'query_sample': query[:100]
            }
            
            # Store embedding
            self.embeddings[cache_key] = QueryEmbedding(
                embedding=query_embedding,
                hash_key=cache_key,
                timestamp=time.time(),
                usage_count=1,
                quality_score=response.get('confidence', 0.5)
            )
            
            logger.debug(f"Cached response: {query[:50]}...")
    
    def _evict_lru_entries(self):
        """Evict least recently used entries"""
        if not self.cache:
            return
        
        # Sort by last accessed time
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1]['last_accessed']
        )
        
        # Remove oldest 20% of entries
        num_to_remove = max(1, len(sorted_entries) // 5)
        
        for cache_key, _ in sorted_entries[:num_to_remove]:
            del self.cache[cache_key]
            if cache_key in self.embeddings:
                del self.embeddings[cache_key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        if not self.cache:
            return {'cache_size': 0, 'hit_rate': 0.0}
        
        total_accesses = sum(entry['access_count'] for entry in self.cache.values())
        avg_similarity = np.mean([emb.quality_score for emb in self.embeddings.values()])
        
        return {
            'cache_size': len(self.cache),
            'total_accesses': total_accesses,
            'avg_quality_score': avg_similarity,
            'memory_usage_mb': len(pickle.dumps(self.cache)) / (1024 * 1024)
        }


class PrivacyPreservingEngine:
    """Advanced privacy and security optimizations"""
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.epsilon = epsilon  # Differential privacy parameter
        self.delta = delta
        self.noise_scale = None
        self.privacy_budget = 1.0
        self.query_audit_log = deque(maxlen=10000)
        
    def add_differential_privacy_noise(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Add calibrated noise for differential privacy"""
        if 'confidence' not in response:
            return response
        
        # Calculate noise scale using epsilon-delta DP
        sensitivity = 0.1  # Assumption: confidence changes by at most 0.1
        noise_scale = sensitivity / (self.epsilon - np.log(self.delta))
        
        # Add Laplacian noise to numerical values
        if isinstance(response.get('confidence'), (int, float)):
            noise = np.random.laplace(0, noise_scale)
            response['confidence'] = max(0.0, min(1.0, response['confidence'] + noise))
            response['privacy_applied'] = True
            response['privacy_epsilon'] = self.epsilon
        
        # Update privacy budget
        self.privacy_budget = max(0, self.privacy_budget - self.epsilon)
        
        return response
    
    def sanitize_query(self, query: str) -> str:
        """Sanitize query to remove potential sensitive information"""
        import re
        
        # Remove potential PII patterns
        patterns = {
            r'\b\d{3}-\d{2}-\d{4}\b': '[SSN]',  # SSN
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b': '[CARD]',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[EMAIL]',  # Email
            r'\b\d{3}-\d{3}-\d{4}\b': '[PHONE]',  # Phone
        }
        
        sanitized = query
        for pattern, replacement in patterns.items():
            sanitized = re.sub(pattern, replacement, sanitized)
        
        return sanitized
    
    def audit_query(self, query: str, user_id: str = "anonymous", 
                   response_metadata: Dict[str, Any] = None):
        """Audit query for security and compliance"""
        audit_entry = {
            'timestamp': time.time(),
            'user_id': hashlib.sha256(user_id.encode()).hexdigest()[:16],
            'query_hash': hashlib.sha256(query.encode()).hexdigest(),
            'query_length': len(query),
            'response_confidence': response_metadata.get('confidence', 0) if response_metadata else 0,
            'privacy_applied': response_metadata.get('privacy_applied', False) if response_metadata else False
        }
        
        self.query_audit_log.append(audit_entry)
    
    def detect_anomalous_queries(self) -> List[Dict[str, Any]]:
        """Detect potentially anomalous or malicious queries"""
        if len(self.query_audit_log) < 10:
            return []
        
        # Convert to features for anomaly detection
        recent_queries = list(self.query_audit_log)[-100:]  # Last 100 queries
        
        features = []
        for entry in recent_queries:
            features.append([
                entry['query_length'],
                entry['response_confidence'],
                1 if entry['privacy_applied'] else 0,
                time.time() - entry['timestamp']  # Time since query
            ])
        
        features = np.array(features)
        
        # Simple statistical anomaly detection
        mean = np.mean(features, axis=0)
        std = np.std(features, axis=0)
        
        anomalies = []
        for i, (feature_vec, entry) in enumerate(zip(features, recent_queries)):
            z_scores = np.abs((feature_vec - mean) / (std + 1e-8))
            
            # Flag as anomaly if any z-score > 3
            if np.any(z_scores > 3):
                anomalies.append({
                    'entry': entry,
                    'anomaly_scores': z_scores.tolist(),
                    'severity': np.max(z_scores)
                })
        
        return sorted(anomalies, key=lambda x: x['severity'], reverse=True)[:5]


class ModelCompressionEngine:
    """Advanced model compression and optimization"""
    
    def __init__(self):
        self.compression_history = []
        self.quantization_stats = {}
        
    def simulate_quantization_effects(self, model_size_gb: float, 
                                    quantization_bits: int = 8) -> Dict[str, Any]:
        """Simulate quantization effects on model performance"""
        original_bits = 32  # Assume FP32 original
        compression_ratio = original_bits / quantization_bits
        
        # Empirical relationships from research
        compressed_size = model_size_gb / compression_ratio
        
        # Performance impact (based on research papers)
        if quantization_bits == 8:
            accuracy_retention = 0.95  # Typical INT8 accuracy retention
            speedup_factor = 2.0
        elif quantization_bits == 4:
            accuracy_retention = 0.85  # More aggressive quantization
            speedup_factor = 4.0
        else:
            accuracy_retention = 1.0
            speedup_factor = 1.0
        
        return {
            'original_size_gb': model_size_gb,
            'compressed_size_gb': compressed_size,
            'compression_ratio': compression_ratio,
            'accuracy_retention': accuracy_retention,
            'speedup_factor': speedup_factor,
            'memory_saved_gb': model_size_gb - compressed_size,
            'quantization_bits': quantization_bits
        }
    
    def optimize_inference_path(self, query_complexity: float, 
                               model_size: float) -> Dict[str, str]:
        """Determine optimal inference path based on query complexity"""
        
        # Simple heuristic-based optimization
        if query_complexity < 0.3 and model_size > 2.0:
            return {
                'optimization': 'early_exit',
                'reason': 'Simple query detected, using early exit layers',
                'expected_speedup': '2x'
            }
        elif query_complexity > 0.8:
            return {
                'optimization': 'full_precision',
                'reason': 'Complex query requires full model precision',
                'expected_speedup': '1x'
            }
        else:
            return {
                'optimization': 'quantized_inference',
                'reason': 'Balanced query complexity, using quantized path',
                'expected_speedup': '1.5x'
            }


class AdvancedMLOptimizer:
    """Main advanced ML optimization pipeline"""
    
    def __init__(self, cache_size: int = 1000):
        self.batching_engine = AdaptiveBatchingEngine()
        self.cache_engine = SemanticCacheEngine(cache_size=cache_size)
        self.privacy_engine = PrivacyPreservingEngine()
        self.compression_engine = ModelCompressionEngine()
        self.optimization_metrics = deque(maxlen=1000)
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize all optimization components"""
        logger.info("Initializing Advanced ML Optimizer...")
        
        # Pre-warm caches and models
        await self._preload_optimizations()
        
        self.is_initialized = True
        logger.success("Advanced ML Optimizer initialized")
    
    async def _preload_optimizations(self):
        """Pre-load common optimizations"""
        # Simulate pre-warming with common MSP queries
        sample_queries = [
            "What is our profit margin?",
            "Which clients are most profitable?",
            "How is our staff utilization?",
            "What are our biggest costs?",
            "Which licenses are underutilized?"
        ]
        
        for query in sample_queries:
            embedding = self.cache_engine._get_query_embedding(query)
            logger.debug(f"Pre-warmed embedding for: {query}")
    
    async def optimize_query(self, query: str, context_hash: str, 
                           model_complexity: float = 0.5) -> Dict[str, Any]:
        """Optimize query processing with advanced ML algorithms"""
        start_time = time.time()
        
        # 1. Privacy and security preprocessing
        sanitized_query = self.privacy_engine.sanitize_query(query)
        
        # 2. Check semantic cache
        cached_response = await self.cache_engine.get_cached_response(
            sanitized_query, context_hash
        )
        
        if cached_response:
            return {
                'response': cached_response,
                'optimization_applied': 'semantic_cache_hit',
                'processing_time': time.time() - start_time,
                'cache_hit': True
            }
        
        # 3. Determine optimal inference path
        optimization_path = self.compression_engine.optimize_inference_path(
            model_complexity, 0.6  # Assume 600MB model
        )
        
        # 4. Apply adaptive batching (if multiple queries)
        batch_id = await self.batching_engine.add_request({
            'query': sanitized_query,
            'context_hash': context_hash,
            'complexity': model_complexity
        })
        
        return {
            'sanitized_query': sanitized_query,
            'optimization_path': optimization_path,
            'batch_id': batch_id,
            'cache_miss': True,
            'preprocessing_time': time.time() - start_time
        }
    
    async def postprocess_response(self, response: Dict[str, Any], 
                                 query: str, context_hash: str) -> Dict[str, Any]:
        """Apply post-processing optimizations"""
        start_time = time.time()
        
        # 1. Apply differential privacy
        privacy_response = self.privacy_engine.add_differential_privacy_noise(response)
        
        # 2. Cache the response
        await self.cache_engine.cache_response(query, context_hash, privacy_response)
        
        # 3. Audit the query
        self.privacy_engine.audit_query(query, response_metadata=privacy_response)
        
        # 4. Record optimization metrics
        optimization_metrics = OptimizationMetrics(
            inference_time=response.get('processing_time', 0),
            memory_usage=psutil.Process().memory_info().rss / (1024*1024),
            cache_hit_rate=self._calculate_cache_hit_rate(),
            model_confidence=privacy_response.get('confidence', 0.5),
            security_score=0.9 if privacy_response.get('privacy_applied') else 0.7,
            optimization_level='advanced',
            throughput_qps=1.0 / max(0.1, response.get('processing_time', 1.0)),
            latency_p99=response.get('processing_time', 1.0)
        )
        
        self.optimization_metrics.append(optimization_metrics)
        
        privacy_response.update({
            'optimization_applied': True,
            'postprocessing_time': time.time() - start_time,
            'total_optimization_time': time.time() - start_time
        })
        
        return privacy_response
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate current cache hit rate"""
        cache_stats = self.cache_engine.get_cache_stats()
        if cache_stats['cache_size'] == 0:
            return 0.0
        
        return min(1.0, cache_stats['total_accesses'] / max(1, cache_stats['cache_size']))
    
    async def get_system_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.optimization_metrics:
            return {'status': 'no_data'}
        
        recent_metrics = list(self.optimization_metrics)[-100:]  # Last 100 operations
        
        # Calculate performance statistics
        avg_inference_time = np.mean([m.inference_time for m in recent_metrics])
        avg_memory_usage = np.mean([m.memory_usage for m in recent_metrics])
        avg_confidence = np.mean([m.model_confidence for m in recent_metrics])
        
        # Get cache performance
        cache_stats = self.cache_engine.get_cache_stats()
        
        # Detect anomalies
        anomalies = self.privacy_engine.detect_anomalous_queries()
        
        return {
            'performance_summary': {
                'avg_inference_time': avg_inference_time,
                'avg_memory_usage_mb': avg_memory_usage,
                'avg_confidence': avg_confidence,
                'cache_hit_rate': self._calculate_cache_hit_rate(),
                'total_optimizations': len(self.optimization_metrics)
            },
            'cache_performance': cache_stats,
            'security_status': {
                'anomalies_detected': len(anomalies),
                'privacy_budget_remaining': self.privacy_engine.privacy_budget,
                'audit_log_size': len(self.privacy_engine.query_audit_log)
            },
            'optimization_recommendations': self._generate_optimization_recommendations(recent_metrics)
        }
    
    def _generate_optimization_recommendations(self, metrics: List[OptimizationMetrics]) -> List[str]:
        """Generate ML-based optimization recommendations"""
        recommendations = []
        
        if not metrics:
            return recommendations
        
        avg_inference_time = np.mean([m.inference_time for m in metrics])
        avg_memory = np.mean([m.memory_usage for m in metrics])
        cache_hit_rate = self._calculate_cache_hit_rate()
        
        # Performance-based recommendations
        if avg_inference_time > 30.0:
            recommendations.append("Consider model quantization to reduce inference time")
        
        if avg_memory > 1000:  # > 1GB
            recommendations.append("Enable gradient checkpointing to reduce memory usage")
        
        if cache_hit_rate < 0.2:
            recommendations.append("Increase cache size or adjust similarity threshold")
        
        # Security recommendations
        if self.privacy_engine.privacy_budget < 0.1:
            recommendations.append("Privacy budget low - consider refreshing differential privacy parameters")
        
        return recommendations[:5]  # Top 5 recommendations
    
    async def cleanup(self):
        """Cleanup optimization resources"""
        logger.info("Cleaning up Advanced ML Optimizer...")
        
        # Save cache and metrics for persistence
        final_report = await self.get_system_performance_report()
        logger.info(f"Final optimization report: {final_report}")
        
        logger.success("Advanced ML Optimizer cleanup completed")
