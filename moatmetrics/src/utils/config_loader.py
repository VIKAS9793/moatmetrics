"""
Configuration loader for MoatMetrics.

This module provides utilities for loading and validating configuration.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import json
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseModel):
    """Database configuration schema."""
    url: str = "sqlite:///./data/moatmetrics.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class PathConfig(BaseModel):
    """Path configuration schema."""
    data_raw: Path = Path("./data/raw")
    data_processed: Path = Path("./data/processed")
    data_snapshots: Path = Path("./data/snapshots")
    reports: Path = Path("./reports")
    logs: Path = Path("./logs")
    temp: Path = Path("./temp")
    
    @field_validator('*', mode='before')
    @classmethod
    def convert_to_path(cls, v):
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v


class ETLConfig(BaseModel):
    """ETL configuration schema."""
    batch_size: int = 1000
    validation_strict: bool = True
    snapshot_enabled: bool = True
    max_file_size_mb: int = 100


class AnalyticsConfig(BaseModel):
    """Analytics configuration schema."""
    confidence_threshold: float = Field(0.7, ge=0, le=1)
    enable_shap: bool = True
    max_shap_samples: int = 100
    cache_results: bool = True
    cache_ttl_seconds: int = 3600


class APIConfig(BaseModel):
    """API configuration schema."""
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    rate_limit: int = 100
    rate_limit_window: int = 60


class GovernanceConfig(BaseModel):
    """Governance configuration schema."""
    policy_file: Path = Path("./config/policies/default_policy.json")
    audit_enabled: bool = True
    require_approval_threshold: float = Field(0.5, ge=0, le=1)
    human_in_loop_enabled: bool = True


class ReportingConfig(BaseModel):
    """Reporting configuration schema."""
    default_format: str = "pdf"
    include_audit_trail: bool = True
    include_explanations: bool = True
    max_records_per_report: int = 10000


class LoggingConfig(BaseModel):
    """Logging configuration schema."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_rotation: str = "1 day"
    retention: str = "30 days"


class AgentConfig(BaseModel):
    """Agent configuration schema."""
    schedule_enabled: bool = False
    schedule_cron: str = "0 2 * * *"
    max_retries: int = 3
    retry_delay_seconds: int = 60


class SecurityConfig(BaseModel):
    """Security configuration schema."""
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    bcrypt_rounds: int = 12


class AppConfig(BaseModel):
    """Main application configuration schema."""
    name: str = "MoatMetrics"
    version: str = "1.0.0-prototype"
    environment: str = "development"
    debug: bool = True


class Config(BaseSettings):
    """Complete configuration schema."""
    app: AppConfig = AppConfig()
    database: DatabaseConfig = DatabaseConfig()
    paths: PathConfig = PathConfig()
    etl: ETLConfig = ETLConfig()
    analytics: AnalyticsConfig = AnalyticsConfig()
    api: APIConfig = APIConfig()
    governance: GovernanceConfig = GovernanceConfig()
    reporting: ReportingConfig = ReportingConfig()
    logging: LoggingConfig = LoggingConfig()
    agent: AgentConfig = AgentConfig()
    security: SecurityConfig = SecurityConfig()
    
    class Config:
        """Pydantic config."""
        env_prefix = "MOATMETRICS_"
        env_nested_delimiter = "__"


class ConfigLoader:
    """Configuration loader and manager."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or "./config/config.yaml"
        self._config: Optional[Config] = None
        self._policy: Optional[Dict[str, Any]] = None
    
    def load_config(self) -> Config:
        """
        Load configuration from file.
        
        Returns:
            Configuration object
        """
        if self._config is not None:
            return self._config
        
        config_data = {}
        
        # Load YAML configuration
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f) or {}
        
        # Create config object (will also load from environment variables)
        self._config = Config(**config_data)
        
        # Ensure all paths exist
        self._create_directories()
        
        return self._config
    
    def load_policy(self) -> Dict[str, Any]:
        """
        Load governance policy.
        
        Returns:
            Policy dictionary
        """
        if self._policy is not None:
            return self._policy
        
        config = self.load_config()
        policy_file = config.governance.policy_file
        
        if policy_file.exists():
            with open(policy_file, "r") as f:
                self._policy = json.load(f)
        else:
            # Default minimal policy
            self._policy = {
                "version": "1.0.0",
                "roles": {
                    "admin": {
                        "permissions": ["*"]
                    }
                },
                "data_governance": {
                    "retention_days": 365,
                    "allowed_file_types": ["csv", "xlsx", "json"]
                }
            }
        
        return self._policy
    
    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        if not self._config:
            return
        
        paths = [
            self._config.paths.data_raw,
            self._config.paths.data_processed,
            self._config.paths.data_snapshots,
            self._config.paths.reports,
            self._config.paths.logs,
            self._config.paths.temp
        ]
        
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)
    
    def get_database_url(self) -> str:
        """Get database URL."""
        config = self.load_config()
        return config.database.url
    
    def get_api_settings(self) -> Dict[str, Any]:
        """Get API settings for FastAPI."""
        config = self.load_config()
        return {
            "title": config.app.name,
            "version": config.app.version,
            "debug": config.app.debug,
            "host": config.api.host,
            "port": config.api.port
        }


# Global configuration instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Get configuration loader instance.
    
    Args:
        config_path: Optional path to configuration file
    
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_path)
    return _config_loader


def get_config() -> Config:
    """
    Get configuration object.
    
    Returns:
        Configuration object
    """
    loader = get_config_loader()
    return loader.load_config()


def get_policy() -> Dict[str, Any]:
    """
    Get governance policy.
    
    Returns:
        Policy dictionary
    """
    loader = get_config_loader()
    return loader.load_policy()
