"""
Logging configuration for MoatMetrics.

This module provides centralized logging configuration using loguru.
"""

import sys
from pathlib import Path
from loguru import logger
import yaml


def setup_logging(config_path: str = "./config/config.yaml") -> None:
    """
    Configure logging for the application.
    
    Args:
        config_path: Path to configuration file
    """
    # Load configuration
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            logging_config = config.get("logging", {})
    except Exception:
        # Default configuration if config file not found
        logging_config = {
            "level": "INFO",
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            "file_rotation": "1 day",
            "retention": "30 days"
        }
    
    # Remove default logger
    logger.remove()
    
    # Console logging
    logger.add(
        sys.stdout,
        level=logging_config.get("level", "INFO"),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # File logging
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "moatmetrics_{time:YYYY-MM-DD}.log",
        level=logging_config.get("level", "INFO"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=logging_config.get("file_rotation", "1 day"),
        retention=logging_config.get("retention", "30 days"),
        compression="zip",
        enqueue=True  # Thread-safe logging
    )
    
    # Separate error log
    logger.add(
        log_dir / "errors_{time:YYYY-MM-DD}.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        rotation="1 week",
        retention="90 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True
    )
    
    logger.info("Logging configured successfully")


def get_logger(name: str):
    """
    Get a logger instance with context.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logger.bind(name=name)
