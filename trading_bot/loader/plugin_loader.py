"""
Strategy Plugin Loader for Trading Bot

Loads external agent packages by path with syntax:
<pip-style pkg>.<module>:<Class>

Features:
- Auto-pip-install if package missing
- Cache imports to avoid reload
- Support for both local and external packages
"""

import importlib
import importlib.util
import subprocess
import sys
import os
import venv
from typing import Dict, Type, Any, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cache for loaded classes
_CLASS_CACHE: Dict[str, Type] = {}


class PluginLoaderError(Exception):
    """Custom exception for plugin loading errors."""
    pass


def _ensure_venv_pip(package_name: str) -> bool:
    """
    Try to auto-install a package if missing.
    
    Args:
        package_name: The pip package name to install
        
    Returns:
        True if installation successful, False otherwise
    """
    try:
        logger.info(f"Attempting to install missing package: {package_name}")
        
        # Use the current Python's pip
        cmd = [sys.executable, "-m", "pip", "install", package_name]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully installed {package_name}")
            return True
        else:
            logger.error(f"Failed to install {package_name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout installing {package_name}")
        return False
    except Exception as e:
        logger.error(f"Error installing {package_name}: {e}")
        return False


def _parse_path(path: str) -> tuple[str, str, str]:
    """
    Parse path syntax: <pip-style pkg>.<module>:<Class>
    
    Args:
        path: Path string like "trading_bot.agents.sma_agent:SMAAgent"
              or "ai-hedge-fund.strategies.momentum:MomentumStrategy"
    
    Returns:
        Tuple of (package_name, module_path, class_name)
    
    Raises:
        PluginLoaderError: If path format is invalid
    """
    if ":" not in path:
        raise PluginLoaderError(f"Invalid path format '{path}'. Expected '<pkg>.<module>:<Class>'")
    
    module_path, class_name = path.split(":", 1)
    
    if "." not in module_path:
        raise PluginLoaderError(f"Invalid module path '{module_path}'. Expected '<pkg>.<module>'")
    
    # Split package and module
    parts = module_path.split(".")
    if len(parts) < 2:
        raise PluginLoaderError(f"Invalid module path '{module_path}'. Need at least package.module")
    
    # For packages like ai-hedge-fund, treat the first part as package name
    package_name = parts[0]
    
    return package_name, module_path, class_name


def _import_module_with_fallback(module_path: str, package_name: str) -> Any:
    """
    Import a module with fallback to auto-installation.
    
    Args:
        module_path: Full module path like "trading_bot.agents.sma_agent"
        package_name: Package name for pip install like "trading_bot" or "ai-hedge-fund"
    
    Returns:
        The imported module
        
    Raises:
        PluginLoaderError: If import fails even after installation attempt
    """
    try:
        # First attempt: direct import
        module = importlib.import_module(module_path)
        return module
        
    except ImportError as e:
        logger.warning(f"Failed to import {module_path}: {e}")
        
        # Handle package names with dashes (convert to underscores for import)
        normalized_module_path = module_path.replace("-", "_")
        if normalized_module_path != module_path:
            try:
                logger.info(f"Trying normalized path: {normalized_module_path}")
                module = importlib.import_module(normalized_module_path)
                return module
            except ImportError:
                pass
        
        # Second attempt: try auto-installation
        if package_name not in sys.modules:
            logger.info(f"Package {package_name} not found, attempting installation...")
            
            if _ensure_venv_pip(package_name):
                # Force reload of import caches
                importlib.invalidate_caches()
                
                try:
                    # Try original path again
                    module = importlib.import_module(module_path)
                    return module
                except ImportError:
                    # Try normalized path
                    try:
                        module = importlib.import_module(normalized_module_path)
                        return module
                    except ImportError:
                        pass
        
        # Final failure
        raise PluginLoaderError(
            f"Failed to import module '{module_path}' even after installation attempt. "
            f"Original error: {e}"
        )


def load_strategy(path: str) -> Type:
    """
    Load a strategy class from the given path.
    
    Args:
        path: Path string in format "<pip-style pkg>.<module>:<Class>"
              Examples:
              - "trading_bot.agents.sma_agent:SMAAgent"
              - "ai-hedge-fund.strategies.momentum:MomentumStrategy"
              - "external.ai_hedge_fund.strategies.base:BaseStrategy"
    
    Returns:
        The loaded strategy class
        
    Raises:
        PluginLoaderError: If loading fails
    """
    # Check cache first
    if path in _CLASS_CACHE:
        logger.debug(f"Returning cached class for {path}")
        return _CLASS_CACHE[path]
    
    try:
        # Parse the path
        package_name, module_path, class_name = _parse_path(path)
        
        logger.info(f"Loading strategy: {class_name} from {module_path}")
        
        # Import the module (with auto-install fallback)
        module = _import_module_with_fallback(module_path, package_name)
        
        # Get the class from the module
        if not hasattr(module, class_name):
            raise PluginLoaderError(
                f"Class '{class_name}' not found in module '{module_path}'. "
                f"Available attributes: {dir(module)}"
            )
        
        strategy_class = getattr(module, class_name)
        
        # Verify it's a class
        if not isinstance(strategy_class, type):
            raise PluginLoaderError(f"'{class_name}' is not a class in {module_path}")
        
        # Cache the result
        _CLASS_CACHE[path] = strategy_class
        
        logger.info(f"Successfully loaded {class_name} from {module_path}")
        return strategy_class
        
    except Exception as e:
        if isinstance(e, PluginLoaderError):
            raise
        else:
            raise PluginLoaderError(f"Unexpected error loading strategy '{path}': {e}")


def clear_cache() -> None:
    """Clear the import cache. Useful for testing or forced reloads."""
    global _CLASS_CACHE
    _CLASS_CACHE.clear()
    logger.info("Plugin loader cache cleared")


def get_cached_strategies() -> Dict[str, Type]:
    """Get all currently cached strategy classes."""
    return _CLASS_CACHE.copy()


def is_strategy_cached(path: str) -> bool:
    """Check if a strategy is already cached."""
    return path in _CLASS_CACHE


# Convenience functions for common local strategies
def load_sma_agent():
    """Load the SMA agent strategy."""
    return load_strategy("trading_bot.agents.sma_agent:SMAAgent")


def load_github_agent():
    """Load the GitHub agent strategy."""
    return load_strategy("trading_bot.agents.github_agent:GitHubAgent")


def load_technical_agent():
    """Load the optimized technical agent strategy."""
    return load_strategy("trading_bot.agents.optimized_technicals:OptimizedTechnicalAgent")


# External strategy loaders (examples)
def load_ai_hedge_fund_strategy(strategy_name: str = "base"):
    """
    Load a strategy from the ai-hedge-fund external package.
    
    Args:
        strategy_name: Name of the strategy to load (default: "base")
    """
    path = f"external.ai_hedge_fund.strategies.{strategy_name}:Strategy"
    return load_strategy(path)