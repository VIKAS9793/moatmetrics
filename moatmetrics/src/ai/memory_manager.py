"""
MoatMetrics AI Memory Manager
Production-grade, memory-efficient Ollama model management with checkpointing
"""
import asyncio
import json
import time
import gc
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import psutil
import joblib
from loguru import logger
import aiohttp
from asyncio_throttle import Throttler
import platform


@dataclass
class ModelInfo:
    """Model metadata for memory management"""
    name: str
    size_gb: float
    last_used: float
    load_time: float
    usage_count: int
    priority: int
    status: str = "unloaded"  # unloaded, loading, loaded, unloading


class OllamaClient:
    """Async Ollama client for model operations"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or 'http://localhost:11434'
        try:
            from ..utils.config_loader import get_config
            config = get_config()
            if hasattr(config, 'ai') and hasattr(config.ai, 'ollama_base_url'):
                self.base_url = config.ai.ollama_base_url
        except Exception as e:
            print(f"Warning: Could not load Ollama config: {e}")
        self.session: Optional[aiohttp.ClientSession] = None
        self.throttler = Throttler(rate_limit=20, period=60)  # Increased rate limit
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def chat(self, model: str, messages: List[Dict], stream: bool = False) -> Dict:
        """Send chat request to Ollama"""
        await self._ensure_session()
        async with self.throttler:
            try:
                payload = {
                    "model": model,
                    "messages": messages,
                    "stream": stream
                }
                async with self.session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"Ollama error: {response.status}")
            except Exception as e:
                logger.error(f"Ollama chat error: {e}")
                raise
    
    async def pull_model(self, model: str) -> bool:
        """Pull model from Ollama registry"""
        await self._ensure_session()
        try:
            payload = {"name": model}
            async with self.session.post(
                f"{self.base_url}/api/pull",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=1800)  # 30min timeout
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Model pull error: {e}")
            return False
    
    async def list_models(self) -> List[Dict]:
        """List available models"""
        await self._ensure_session()
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("models", [])
                return []
        except Exception as e:
            logger.error(f"List models error: {e}")
            return []
    
    async def _ensure_session(self):
        """Ensure aiohttp session is available"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()


class AIMemoryManager:
    """Memory-aware AI model manager with checkpointing"""
    
    def __init__(self, max_memory_gb: Optional[float] = None, state_file: str = "ai_memory_state.json"):
        self.max_memory_gb = max_memory_gb or self._detect_max_memory()
        self.state_file = Path(state_file)
        self.loaded_models: Dict[str, ModelInfo] = {}
        self.loading_lock = asyncio.Lock()
        self.ollama = OllamaClient()
        
        # Detect hardware capabilities for smart model selection
        self.hardware = self._detect_hardware_capabilities()
        
        # Model specifications (memory requirements)
        # Only approved model: tinyllama (600MB) - works on all hardware
        # This is the only model approved for production use
        self.model_specs = {
            'tinyllama': ModelInfo('tinyllama', 0.6, 0, 0, 0, 1),  # Primary approved model
        }
        
        # Set approved model as primary
        self.primary_model = 'tinyllama'
        self.approved_models = ['tinyllama']
        
        # Load previous state
        self._load_state()
        
        logger.info(f"AI Memory Manager initialized - Max memory: {self.max_memory_gb:.1f}GB, Hardware: {self.hardware['tier']}")
    
    def _detect_max_memory(self) -> float:
        """Detect available memory with buffer for OS"""
        total_memory_gb = psutil.virtual_memory().total / (1024**3)
        # Reserve 20% for OS and other processes
        available = total_memory_gb * 0.8
        logger.info(f"Detected {total_memory_gb:.1f}GB total, {available:.1f}GB available for AI")
        return available
    
    def _detect_hardware_capabilities(self) -> Dict[str, Any]:
        """Detect hardware capabilities for model selection"""
        try:
            cpu_count = psutil.cpu_count(logical=True)
            memory_gb = psutil.virtual_memory().total / (1024**3)
            
            # Basic GPU detection (simplified)
            has_gpu = False
            try:
                import subprocess
                result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
                has_gpu = result.returncode == 0
            except:
                pass
            
            # Determine hardware tier
            if has_gpu and memory_gb >= 16:
                tier = 'high_end'  # Can run larger models
            elif memory_gb >= 8:
                tier = 'medium'    # Can run phi3:mini
            else:
                tier = 'low_end'   # Stick to tinyllama
            
            capabilities = {
                'cpu_count': cpu_count,
                'memory_gb': memory_gb,
                'has_gpu': has_gpu,
                'tier': tier,
                'platform': platform.system()
            }
            
            logger.info(f"Hardware capabilities: {tier} tier, {cpu_count} CPUs, {memory_gb:.1f}GB RAM, GPU: {has_gpu}")
            return capabilities
            
        except Exception as e:
            logger.warning(f"Hardware detection failed: {e}, defaulting to low_end")
            return {'tier': 'low_end', 'cpu_count': 1, 'memory_gb': 4, 'has_gpu': False, 'platform': 'Unknown'}
    
    def _load_state(self):
        """Load previous memory state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state_data = json.load(f)
                    for model_name, model_data in state_data.get('loaded_models', {}).items():
                        self.loaded_models[model_name] = ModelInfo(**model_data)
                logger.info(f"Loaded previous state: {len(self.loaded_models)} models")
            except Exception as e:
                logger.warning(f"Failed to load state: {e}")
    
    def _save_state(self):
        """Save current memory state"""
        try:
            state_data = {
                'loaded_models': {name: asdict(info) for name, info in self.loaded_models.items()},
                'last_saved': time.time()
            }
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            logger.debug("Memory state saved")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def _get_current_memory_usage(self) -> float:
        """Get current memory usage of loaded models"""
        return sum(model.size_gb for model in self.loaded_models.values() if model.status == "loaded")
    
    async def _free_memory_for_model(self, required_gb: float):
        """Free memory by unloading least important models"""
        current_usage = self._get_current_memory_usage()
        target_usage = self.max_memory_gb - required_gb
        
        if current_usage <= target_usage:
            return  # Enough memory available
        
        # Sort models by priority (lowest first), then by last_used
        models_to_unload = sorted(
            [(name, model) for name, model in self.loaded_models.items() if model.status == "loaded"],
            key=lambda x: (x[1].priority, x[1].last_used)
        )
        
        freed_memory = 0
        for model_name, model_info in models_to_unload:
            if current_usage - freed_memory <= target_usage:
                break
                
            logger.info(f"Unloading {model_name} to free {model_info.size_gb:.1f}GB")
            model_info.status = "unloaded"
            freed_memory += model_info.size_gb
            
            # Force garbage collection
            gc.collect()
    
    async def smart_model_load(self, model_name: str) -> bool:
        """Intelligently load model with memory management"""
        async with self.loading_lock:
            # Check if already loaded
            if model_name in self.loaded_models and self.loaded_models[model_name].status == "loaded":
                self.loaded_models[model_name].last_used = time.time()
                self.loaded_models[model_name].usage_count += 1
                self._save_state()
                return True
            
            # Get model specs
            if model_name not in self.model_specs:
                logger.error(f"Unknown model: {model_name}")
                return False
            
            model_info = self.model_specs[model_name]
            required_memory = model_info.size_gb
            
            # Check memory availability
            current_memory = self._get_current_memory_usage()
            if current_memory + required_memory > self.max_memory_gb:
                logger.info(f"Freeing memory for {model_name} ({required_memory:.1f}GB)")
                await self._free_memory_for_model(required_memory)
            
            # Load the model
            try:
                logger.info(f"Loading {model_name}...")
                model_info.status = "loading"
                start_time = time.time()
                
                # Test model with simple query
                response = await self.ollama.chat(
                    model=model_name,
                    messages=[{'role': 'user', 'content': 'Hello'}]
                )
                
                load_time = time.time() - start_time
                
                # Update tracking
                model_info.last_used = time.time()
                model_info.load_time = load_time
                model_info.usage_count += 1
                model_info.status = "loaded"
                
                self.loaded_models[model_name] = model_info
                self._save_state()
                
                logger.success(f"Loaded {model_name} in {load_time:.2f}s")
                return True
                
            except Exception as e:
                model_info.status = "unloaded"
                logger.error(f"Failed to load {model_name}: {e}")
                return False
    
    async def get_optimal_model(self, task_type: str, urgency: str = "normal") -> str:
        """Select optimal model - always returns tinyllama (only approved model)"""
        # Only tinyllama is approved for use
        model_name = 'tinyllama'
        
        # Check if already loaded for urgent requests
        if urgency == "high" and model_name in self.loaded_models and self.loaded_models[model_name].status == "loaded":
            logger.info(f"Using already loaded approved model {model_name} for urgent request")
            return model_name
        
        logger.info(f"Selected approved model {model_name} for task '{task_type}'")
        return model_name
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory and hardware statistics"""
        system_memory = psutil.virtual_memory()
        ai_memory = self._get_current_memory_usage()
        
        return {
            "system_memory_total_gb": system_memory.total / (1024**3),
            "system_memory_used_gb": system_memory.used / (1024**3),
            "system_memory_percent": system_memory.percent,
            "ai_max_memory_gb": self.max_memory_gb,
            "ai_used_memory_gb": ai_memory,
            "ai_available_memory_gb": self.max_memory_gb - ai_memory,
            "loaded_models": len([m for m in self.loaded_models.values() if m.status == "loaded"]),
            "total_model_usage": sum(m.usage_count for m in self.loaded_models.values()),
            "hardware_tier": self.hardware['tier'],
            "cpu_count": self.hardware['cpu_count'],
            "has_gpu": self.hardware['has_gpu'],
            "primary_model": self.primary_model
        }
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware capabilities info"""
        info = self.hardware.copy()
        # Add total memory info for compatibility
        info['total_memory_gb'] = info.get('memory_gb', 0)
        return info
    
    async def initialize(self) -> bool:
        """Initialize AI Memory Manager and ensure approved model is loaded"""
        try:
            logger.info("Initializing AI Memory Manager...")
            # Test Ollama connectivity
            ollama_status = await self.check_ollama_status()
            if not ollama_status:
                logger.error("Ollama service not available - AI functionality will be limited")
                return False
            
            # Ensure approved model (tinyllama) is loaded
            logger.info(f"Ensuring approved model '{self.primary_model}' is loaded...")
            model_loaded = await self.smart_model_load(self.primary_model)
            
            if model_loaded:
                logger.success(f"Approved model '{self.primary_model}' loaded successfully")
                return True
            else:
                logger.error(f"Failed to load approved model '{self.primary_model}'")
                return False
                
        except Exception as e:
            logger.error(f"AI Memory Manager initialization failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.ollama.close()
        self._save_state()
        logger.info("AI Memory Manager cleanup completed")
    
    async def check_ollama_status(self) -> bool:
        """Check if Ollama service is available"""
        try:
            await self.ollama._ensure_session()
            async with self.ollama.session.get(f"{self.ollama.base_url}/") as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"Ollama status check failed: {e}")
            return False
    
    def _get_recommended_model(self) -> str:
        """Get recommended model - always returns tinyllama (only approved model)"""
        return 'tinyllama'
    
    async def check_model_availability(self, model_name: str) -> bool:
        """Check if a model is available for loading"""
        return model_name in self.model_specs
