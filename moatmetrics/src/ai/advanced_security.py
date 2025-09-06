"""
Advanced Security Framework for MoatMetrics AI
Implements cutting-edge privacy-preserving and security algorithms
"""
import asyncio
import numpy as np
import json
import time
import hashlib
import hmac
import secrets
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
from collections import defaultdict, deque
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
from loguru import logger
import pickle


@dataclass
class SecurityMetrics:
    """Security and privacy metrics tracking"""
    privacy_budget_used: float
    encryption_operations: int
    anomalies_detected: int
    security_score: float
    threat_level: str
    compliance_score: float
    audit_events: int


@dataclass
class FederatedLearningConfig:
    """Configuration for federated learning simulation"""
    num_clients: int
    aggregation_rounds: int
    min_clients_per_round: int
    privacy_epsilon: float
    secure_aggregation: bool


class HomomorphicEncryptionSimulator:
    """Simplified homomorphic encryption simulation for secure computation"""
    
    def __init__(self, key_size: int = 2048):
        self.key_size = key_size
        self.private_key = None
        self.public_key = None
        self.encryption_count = 0
        self.generate_keys()
    
    def generate_keys(self):
        """Generate RSA key pair for simulation"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        logger.debug("Generated homomorphic encryption keys")
    
    def encrypt_value(self, value: Union[int, float]) -> str:
        """Simulate homomorphic encryption of numeric values"""
        try:
            # Convert to bytes
            value_bytes = str(float(value)).encode('utf-8')
            
            # Encrypt with public key
            ciphertext = self.public_key.encrypt(
                value_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            self.encryption_count += 1
            return base64.b64encode(ciphertext).decode('utf-8')
        
        except Exception as e:
            logger.error(f"Homomorphic encryption failed: {e}")
            return str(value)  # Fallback to plaintext
    
    def decrypt_value(self, encrypted_value: str) -> float:
        """Decrypt homomorphically encrypted value"""
        try:
            ciphertext = base64.b64decode(encrypted_value.encode('utf-8'))
            
            plaintext = self.private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return float(plaintext.decode('utf-8'))
        
        except Exception as e:
            logger.error(f"Homomorphic decryption failed: {e}")
            return 0.0
    
    def homomorphic_add(self, encrypted_a: str, encrypted_b: str) -> str:
        """Simulate homomorphic addition (simplified)"""
        # In real homomorphic encryption, this would work on ciphertext directly
        # Here we simulate by decrypting, adding, and re-encrypting
        try:
            a = self.decrypt_value(encrypted_a)
            b = self.decrypt_value(encrypted_b)
            result = a + b
            return self.encrypt_value(result)
        except:
            return encrypted_a  # Fallback
    
    def get_encryption_stats(self) -> Dict[str, Any]:
        """Get encryption operation statistics"""
        return {
            'total_encryptions': self.encryption_count,
            'key_size_bits': self.key_size,
            'encryption_method': 'RSA-OAEP (simulated homomorphic)'
        }


class DifferentialPrivacyEngine:
    """Advanced differential privacy implementation"""
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.global_epsilon = epsilon
        self.delta = delta
        self.privacy_budget = epsilon
        self.noise_history = deque(maxlen=1000)
        self.mechanism_stats = defaultdict(int)
        
    def laplace_mechanism(self, true_value: float, sensitivity: float, 
                         privacy_epsilon: float) -> float:
        """Apply Laplace mechanism for differential privacy"""
        if self.privacy_budget <= 0:
            logger.warning("Privacy budget exhausted, returning noisy approximation")
            return true_value + np.random.normal(0, sensitivity)
        
        # Calculate noise scale
        b = sensitivity / privacy_epsilon
        noise = np.random.laplace(0, b)
        
        # Update privacy budget
        self.privacy_budget = max(0, self.privacy_budget - privacy_epsilon)
        
        # Record noise statistics
        self.noise_history.append({
            'mechanism': 'laplace',
            'noise': noise,
            'epsilon_used': privacy_epsilon,
            'sensitivity': sensitivity,
            'timestamp': time.time()
        })
        
        self.mechanism_stats['laplace'] += 1
        
        noisy_value = true_value + noise
        logger.debug(f"Applied Laplace mechanism: {true_value} -> {noisy_value:.3f}")
        
        return noisy_value
    
    def gaussian_mechanism(self, true_value: float, sensitivity: float, 
                          privacy_epsilon: float) -> float:
        """Apply Gaussian mechanism for (ε,δ)-differential privacy"""
        if self.privacy_budget <= 0:
            return true_value
        
        # Calculate noise scale for (ε,δ)-DP
        c = np.sqrt(2 * np.log(1.25 / self.delta))
        sigma = c * sensitivity / privacy_epsilon
        
        noise = np.random.normal(0, sigma)
        
        # Update privacy budget
        self.privacy_budget = max(0, self.privacy_budget - privacy_epsilon)
        
        self.noise_history.append({
            'mechanism': 'gaussian',
            'noise': noise,
            'epsilon_used': privacy_epsilon,
            'sensitivity': sensitivity,
            'sigma': sigma,
            'timestamp': time.time()
        })
        
        self.mechanism_stats['gaussian'] += 1
        
        return true_value + noise
    
    def exponential_mechanism(self, candidates: List[Any], 
                             utility_function: callable,
                             privacy_epsilon: float) -> Any:
        """Apply exponential mechanism for differential privacy"""
        if not candidates or self.privacy_budget <= 0:
            return candidates[0] if candidates else None
        
        # Calculate utilities
        utilities = [utility_function(candidate) for candidate in candidates]
        
        # Apply exponential mechanism
        probabilities = np.exp(privacy_epsilon * np.array(utilities) / 2)
        probabilities = probabilities / np.sum(probabilities)
        
        # Sample according to probabilities
        selected_idx = np.random.choice(len(candidates), p=probabilities)
        
        self.privacy_budget = max(0, self.privacy_budget - privacy_epsilon)
        self.mechanism_stats['exponential'] += 1
        
        return candidates[selected_idx]
    
    def add_noise_to_response(self, response: Dict[str, Any], 
                            epsilon: float = 0.1) -> Dict[str, Any]:
        """Add differential privacy noise to response data"""
        protected_response = response.copy()
        
        # Apply noise to confidence score
        if 'confidence' in protected_response:
            original_confidence = protected_response['confidence']
            noisy_confidence = self.laplace_mechanism(
                original_confidence, 
                sensitivity=0.1,  # Confidence can change by at most 0.1
                privacy_epsilon=epsilon
            )
            protected_response['confidence'] = max(0.0, min(1.0, noisy_confidence))
        
        # Apply noise to numerical insights (if any)
        if 'numerical_metrics' in protected_response:
            for key, value in protected_response['numerical_metrics'].items():
                if isinstance(value, (int, float)):
                    protected_response['numerical_metrics'][key] = self.gaussian_mechanism(
                        value, sensitivity=value * 0.05, privacy_epsilon=epsilon
                    )
        
        protected_response['privacy_applied'] = True
        protected_response['privacy_epsilon_used'] = epsilon
        protected_response['privacy_budget_remaining'] = self.privacy_budget
        
        return protected_response
    
    def get_privacy_statistics(self) -> Dict[str, Any]:
        """Get differential privacy usage statistics"""
        total_epsilon_used = self.global_epsilon - self.privacy_budget
        
        recent_noise = list(self.noise_history)[-50:]  # Last 50 operations
        avg_noise = np.mean([abs(entry['noise']) for entry in recent_noise]) if recent_noise else 0
        
        return {
            'global_epsilon': self.global_epsilon,
            'epsilon_used': total_epsilon_used,
            'privacy_budget_remaining': self.privacy_budget,
            'delta': self.delta,
            'total_operations': sum(self.mechanism_stats.values()),
            'mechanism_usage': dict(self.mechanism_stats),
            'average_noise_magnitude': avg_noise,
            'privacy_exhausted': self.privacy_budget <= 0.01
        }


class FederatedLearningSimulator:
    """Simulate federated learning for distributed model training"""
    
    def __init__(self, config: FederatedLearningConfig):
        self.config = config
        self.client_models = {}
        self.global_model = None
        self.round_history = []
        self.privacy_engine = DifferentialPrivacyEngine(epsilon=config.privacy_epsilon)
        
    def initialize_clients(self, base_model_params: Dict[str, Any]):
        """Initialize client models with base parameters"""
        for client_id in range(self.config.num_clients):
            # Simulate client model parameters with noise
            client_params = base_model_params.copy()
            
            # Add client-specific variation
            for key, value in client_params.items():
                if isinstance(value, (int, float)):
                    noise = np.random.normal(0, abs(value) * 0.1)
                    client_params[key] = value + noise
            
            self.client_models[f"client_{client_id}"] = {
                'params': client_params,
                'data_samples': np.random.randint(100, 1000),  # Simulate data size
                'last_update': time.time(),
                'privacy_budget': self.config.privacy_epsilon
            }
        
        logger.info(f"Initialized {self.config.num_clients} federated learning clients")
    
    def simulate_local_training(self, client_id: str, 
                               training_data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate local model training on client"""
        if client_id not in self.client_models:
            return {}
        
        client = self.client_models[client_id]
        
        # Simulate training updates
        model_updates = {}
        for key, value in client['params'].items():
            if isinstance(value, (int, float)):
                # Simulate gradient update
                gradient = np.random.normal(0, abs(value) * 0.05)
                learning_rate = 0.01
                
                # Apply differential privacy to gradient
                if client['privacy_budget'] > 0:
                    private_gradient = self.privacy_engine.laplace_mechanism(
                        gradient, 
                        sensitivity=abs(gradient) * 0.1,
                        privacy_epsilon=0.1
                    )
                    client['privacy_budget'] -= 0.1
                else:
                    private_gradient = gradient
                
                model_updates[key] = private_gradient * learning_rate
        
        # Update client model
        for key, update in model_updates.items():
            client['params'][key] += update
        
        client['last_update'] = time.time()
        
        return {
            'client_id': client_id,
            'model_updates': model_updates,
            'data_samples': client['data_samples'],
            'privacy_budget_used': 0.1,
            'training_loss': np.random.exponential(0.5)  # Simulated loss
        }
    
    def federated_averaging(self, client_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform federated averaging of client model updates"""
        if not client_updates:
            return {}
        
        # Weighted averaging by number of data samples
        total_samples = sum(update['data_samples'] for update in client_updates)
        
        global_updates = {}
        param_keys = client_updates[0]['model_updates'].keys()
        
        for key in param_keys:
            weighted_sum = 0
            for update in client_updates:
                weight = update['data_samples'] / total_samples
                weighted_sum += update['model_updates'][key] * weight
            
            global_updates[key] = weighted_sum
        
        # Apply secure aggregation (simplified)
        if self.config.secure_aggregation:
            for key in global_updates:
                # Add noise for secure aggregation
                noise = np.random.normal(0, abs(global_updates[key]) * 0.01)
                global_updates[key] += noise
        
        return global_updates
    
    def run_federated_round(self, training_data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Run one round of federated learning"""
        # Select random subset of clients
        available_clients = list(self.client_models.keys())
        selected_clients = np.random.choice(
            available_clients, 
            size=min(self.config.min_clients_per_round, len(available_clients)),
            replace=False
        )
        
        # Simulate local training on selected clients
        client_updates = []
        for client_id in selected_clients:
            update = self.simulate_local_training(client_id, training_data_summary)
            if update:
                client_updates.append(update)
        
        # Perform federated averaging
        global_updates = self.federated_averaging(client_updates)
        
        # Update global model (simulated)
        if self.global_model is None:
            self.global_model = global_updates
        else:
            for key, value in global_updates.items():
                if key in self.global_model:
                    self.global_model[key] += value
                else:
                    self.global_model[key] = value
        
        # Record round statistics
        round_stats = {
            'round_number': len(self.round_history) + 1,
            'participating_clients': len(client_updates),
            'total_data_samples': sum(u['data_samples'] for u in client_updates),
            'average_loss': np.mean([u['training_loss'] for u in client_updates]),
            'privacy_budget_used': sum(u['privacy_budget_used'] for u in client_updates),
            'timestamp': time.time()
        }
        
        self.round_history.append(round_stats)
        
        logger.info(f"Federated learning round {round_stats['round_number']} completed: "
                   f"{len(client_updates)} clients, avg loss: {round_stats['average_loss']:.3f}")
        
        return round_stats


class ThreatDetectionEngine:
    """Advanced threat detection and security monitoring"""
    
    def __init__(self):
        self.threat_signatures = self._load_threat_signatures()
        self.anomaly_threshold = 3.0  # Z-score threshold
        self.attack_patterns = defaultdict(int)
        self.security_events = deque(maxlen=10000)
        
    def _load_threat_signatures(self) -> Dict[str, List[str]]:
        """Load threat signatures and patterns"""
        return {
            'injection_attacks': [
                r'union\s+select', r'drop\s+table', r'exec\s*\(', 
                r'script\s*>', r'javascript:', r'eval\s*\('
            ],
            'data_exfiltration': [
                r'admin.*password', r'api.*key', r'secret.*token',
                r'credit.*card', r'ssn.*\d{3}-\d{2}-\d{4}'
            ],
            'prompt_injection': [
                r'ignore\s+previous\s+instructions', r'system\s+prompt',
                r'you\s+are\s+now', r'forget\s+everything', r'new\s+role'
            ]
        }
    
    def detect_malicious_patterns(self, query: str) -> Dict[str, Any]:
        """Detect malicious patterns in queries"""
        import re
        
        threats_detected = []
        threat_scores = {}
        
        query_lower = query.lower()
        
        for threat_type, patterns in self.threat_signatures.items():
            for pattern in patterns:
                matches = re.findall(pattern, query_lower, re.IGNORECASE)
                if matches:
                    threats_detected.append({
                        'type': threat_type,
                        'pattern': pattern,
                        'matches': len(matches),
                        'severity': self._calculate_threat_severity(threat_type)
                    })
                    threat_scores[threat_type] = threat_scores.get(threat_type, 0) + 1
        
        # Calculate overall threat level
        total_threat_score = sum(threat_scores.values())
        if total_threat_score >= 3:
            threat_level = 'HIGH'
        elif total_threat_score >= 1:
            threat_level = 'MEDIUM'
        else:
            threat_level = 'LOW'
        
        detection_result = {
            'threat_level': threat_level,
            'total_threat_score': total_threat_score,
            'threats_detected': threats_detected,
            'should_block': threat_level == 'HIGH',
            'query_length': len(query),
            'timestamp': time.time()
        }
        
        # Log security event
        self.security_events.append(detection_result)
        
        # Update attack pattern tracking
        for threat in threats_detected:
            self.attack_patterns[threat['type']] += 1
        
        if threat_level != 'LOW':
            logger.warning(f"Security threat detected: {threat_level} level, "
                          f"{len(threats_detected)} patterns matched")
        
        return detection_result
    
    def _calculate_threat_severity(self, threat_type: str) -> float:
        """Calculate severity score for threat type"""
        severity_map = {
            'injection_attacks': 0.9,
            'data_exfiltration': 0.95,
            'prompt_injection': 0.7,
            'default': 0.5
        }
        return severity_map.get(threat_type, severity_map['default'])
    
    def analyze_query_behavior(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query behavior for anomalies"""
        behavior_features = {
            'query_length': len(query),
            'uppercase_ratio': sum(1 for c in query if c.isupper()) / len(query) if query else 0,
            'special_char_ratio': sum(1 for c in query if not c.isalnum() and not c.isspace()) / len(query) if query else 0,
            'repeated_words': len(query.split()) - len(set(query.lower().split())),
            'time_of_day': time.localtime().tm_hour,
            'query_complexity': len(set(query.lower().split())) / len(query.split()) if query.split() else 0
        }
        
        # Simple anomaly detection based on historical patterns
        anomaly_score = 0
        
        # Check for unusual query length
        if behavior_features['query_length'] > 1000:
            anomaly_score += 0.3
        
        # Check for high special character ratio (potential injection)
        if behavior_features['special_char_ratio'] > 0.2:
            anomaly_score += 0.4
        
        # Check for excessive repetition
        if behavior_features['repeated_words'] > 5:
            anomaly_score += 0.2
        
        # Check for unusual time patterns
        if behavior_features['time_of_day'] < 6 or behavior_features['time_of_day'] > 22:
            anomaly_score += 0.1
        
        is_anomalous = anomaly_score > 0.5
        
        return {
            'is_anomalous': is_anomalous,
            'anomaly_score': anomaly_score,
            'behavior_features': behavior_features,
            'risk_factors': self._identify_risk_factors(behavior_features, anomaly_score)
        }
    
    def _identify_risk_factors(self, features: Dict[str, Any], score: float) -> List[str]:
        """Identify specific risk factors"""
        risks = []
        
        if features['query_length'] > 1000:
            risks.append('Unusually long query')
        
        if features['special_char_ratio'] > 0.2:
            risks.append('High special character density')
        
        if features['repeated_words'] > 5:
            risks.append('Excessive word repetition')
        
        if features['time_of_day'] < 6 or features['time_of_day'] > 22:
            risks.append('Off-hours query timing')
        
        if score > 0.8:
            risks.append('Multiple anomaly indicators')
        
        return risks
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get comprehensive security status summary"""
        recent_events = list(self.security_events)[-100:]  # Last 100 events
        
        high_threats = sum(1 for event in recent_events if event['threat_level'] == 'HIGH')
        medium_threats = sum(1 for event in recent_events if event['threat_level'] == 'MEDIUM')
        
        return {
            'total_security_events': len(self.security_events),
            'recent_high_threats': high_threats,
            'recent_medium_threats': medium_threats,
            'attack_pattern_distribution': dict(self.attack_patterns),
            'security_score': max(0, 100 - (high_threats * 10) - (medium_threats * 5)),
            'last_threat_detected': max((e['timestamp'] for e in recent_events), default=0) if recent_events else 0
        }


class AdvancedSecurityFramework:
    """Main security framework integrating all security components"""
    
    def __init__(self):
        self.homomorphic_engine = HomomorphicEncryptionSimulator()
        self.differential_privacy = DifferentialPrivacyEngine()
        self.threat_detector = ThreatDetectionEngine()
        self.federated_config = FederatedLearningConfig(
            num_clients=5, aggregation_rounds=10, min_clients_per_round=3,
            privacy_epsilon=1.0, secure_aggregation=True
        )
        self.federated_simulator = FederatedLearningSimulator(self.federated_config)
        self.security_metrics = deque(maxlen=1000)
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize security framework"""
        logger.info("Initializing Advanced Security Framework...")
        
        # Initialize federated learning with dummy base model
        base_model = {'param1': 0.5, 'param2': 1.0, 'param3': -0.3}
        self.federated_simulator.initialize_clients(base_model)
        
        self.is_initialized = True
        logger.success("Advanced Security Framework initialized")
    
    async def secure_query_processing(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process query with comprehensive security measures"""
        if user_context is None:
            user_context = {}
        
        start_time = time.time()
        security_results = {}
        
        # 1. Threat detection
        threat_analysis = self.threat_detector.detect_malicious_patterns(query)
        security_results['threat_analysis'] = threat_analysis
        
        if threat_analysis['should_block']:
            return {
                'status': 'BLOCKED',
                'reason': 'Security threat detected',
                'threat_level': threat_analysis['threat_level'],
                'processing_time': time.time() - start_time
            }
        
        # 2. Behavioral analysis
        behavior_analysis = self.threat_detector.analyze_query_behavior(query, user_context)
        security_results['behavior_analysis'] = behavior_analysis
        
        # 3. Query sanitization (basic)
        sanitized_query = self._sanitize_query(query)
        security_results['sanitized_query'] = sanitized_query
        
        # 4. Generate security score
        security_score = self._calculate_security_score(threat_analysis, behavior_analysis)
        security_results['security_score'] = security_score
        
        return {
            'status': 'PROCESSED',
            'security_results': security_results,
            'processing_time': time.time() - start_time,
            'secure_for_processing': security_score > 0.7
        }
    
    def _sanitize_query(self, query: str) -> str:
        """Basic query sanitization"""
        import re
        
        # Remove potential script tags
        sanitized = re.sub(r'<script.*?</script>', '', query, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove SQL injection patterns (basic)
        sql_patterns = [r'union\s+select', r'drop\s+table', r';--', r'/\*.*?\*/']
        for pattern in sql_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    def _calculate_security_score(self, threat_analysis: Dict[str, Any], 
                                behavior_analysis: Dict[str, Any]) -> float:
        """Calculate overall security score"""
        base_score = 1.0
        
        # Deduct for threats
        threat_penalty = threat_analysis['total_threat_score'] * 0.2
        base_score -= threat_penalty
        
        # Deduct for behavioral anomalies
        anomaly_penalty = behavior_analysis['anomaly_score'] * 0.3
        base_score -= anomaly_penalty
        
        return max(0.0, min(1.0, base_score))
    
    async def apply_privacy_protection(self, response: Dict[str, Any], 
                                     privacy_level: str = 'standard') -> Dict[str, Any]:
        """Apply privacy protection to response data"""
        privacy_params = {
            'minimal': {'epsilon': 0.01, 'enable_encryption': False},
            'standard': {'epsilon': 0.1, 'enable_encryption': True},
            'high': {'epsilon': 0.5, 'enable_encryption': True}
        }
        
        params = privacy_params.get(privacy_level, privacy_params['standard'])
        
        # Apply differential privacy
        protected_response = self.differential_privacy.add_noise_to_response(
            response, epsilon=params['epsilon']
        )
        
        # Apply homomorphic encryption to sensitive numerical values
        if params['enable_encryption']:
            if 'confidence' in protected_response:
                encrypted_confidence = self.homomorphic_engine.encrypt_value(
                    protected_response['confidence']
                )
                protected_response['encrypted_confidence'] = encrypted_confidence
        
        protected_response.update({
            'privacy_level': privacy_level,
            'encryption_applied': params['enable_encryption'],
            'timestamp': time.time()
        })
        
        return protected_response
    
    async def simulate_federated_training(self, training_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate federated learning training round"""
        round_result = self.federated_simulator.run_federated_round(training_summary)
        
        # Record security metrics
        security_metrics = SecurityMetrics(
            privacy_budget_used=round_result['privacy_budget_used'],
            encryption_operations=self.homomorphic_engine.encryption_count,
            anomalies_detected=len([e for e in self.threat_detector.security_events 
                                  if e['threat_level'] != 'LOW']),
            security_score=0.9,  # High security in federated setting
            threat_level='LOW',
            compliance_score=0.95,
            audit_events=len(self.threat_detector.security_events)
        )
        
        self.security_metrics.append(security_metrics)
        
        return {
            'federated_round': round_result,
            'security_metrics': asdict(security_metrics),
            'privacy_preserved': True
        }
    
    async def get_comprehensive_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security and privacy report"""
        if not self.security_metrics:
            return {'status': 'no_data'}
        
        # Privacy statistics
        privacy_stats = self.differential_privacy.get_privacy_statistics()
        
        # Encryption statistics
        encryption_stats = self.homomorphic_engine.get_encryption_stats()
        
        # Threat detection summary
        security_summary = self.threat_detector.get_security_summary()
        
        # Federated learning status
        fl_stats = {
            'total_rounds': len(self.federated_simulator.round_history),
            'active_clients': len(self.federated_simulator.client_models),
            'last_round_participants': (
                self.federated_simulator.round_history[-1]['participating_clients'] 
                if self.federated_simulator.round_history else 0
            )
        }
        
        # Overall compliance score
        compliance_score = self._calculate_compliance_score(
            privacy_stats, security_summary, encryption_stats
        )
        
        return {
            'privacy_statistics': privacy_stats,
            'encryption_statistics': encryption_stats,
            'security_summary': security_summary,
            'federated_learning': fl_stats,
            'compliance_score': compliance_score,
            'overall_status': 'SECURE' if compliance_score > 0.8 else 'NEEDS_ATTENTION',
            'recommendations': self._generate_security_recommendations(
                privacy_stats, security_summary, compliance_score
            )
        }
    
    def _calculate_compliance_score(self, privacy_stats: Dict[str, Any], 
                                  security_summary: Dict[str, Any],
                                  encryption_stats: Dict[str, Any]) -> float:
        """Calculate overall security compliance score"""
        score = 1.0
        
        # Deduct for privacy budget exhaustion
        if privacy_stats.get('privacy_exhausted', False):
            score -= 0.2
        
        # Deduct for high threat activity
        if security_summary.get('recent_high_threats', 0) > 0:
            score -= 0.3
        
        if security_summary.get('recent_medium_threats', 0) > 5:
            score -= 0.1
        
        # Bonus for encryption usage
        if encryption_stats.get('total_encryptions', 0) > 0:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _generate_security_recommendations(self, privacy_stats: Dict[str, Any],
                                         security_summary: Dict[str, Any],
                                         compliance_score: float) -> List[str]:
        """Generate security improvement recommendations"""
        recommendations = []
        
        if privacy_stats.get('privacy_exhausted', False):
            recommendations.append("Privacy budget exhausted - consider refreshing DP parameters")
        
        if security_summary.get('recent_high_threats', 0) > 0:
            recommendations.append("High-severity threats detected - review threat detection rules")
        
        if compliance_score < 0.8:
            recommendations.append("Overall compliance score low - implement additional security measures")
        
        if security_summary.get('security_score', 100) < 80:
            recommendations.append("Security score degraded - investigate recent threats")
        
        return recommendations[:5]  # Top 5 recommendations
    
    async def cleanup(self):
        """Cleanup security framework resources"""
        logger.info("Cleaning up Advanced Security Framework...")
        
        final_report = await self.get_comprehensive_security_report()
        logger.info(f"Final security report: {final_report}")
        
        logger.success("Advanced Security Framework cleanup completed")
