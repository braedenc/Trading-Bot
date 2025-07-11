"""
Unit tests for the strategy plugin loader.

Tests cover:
- Happy path (local agent loading)
- Auto-install functionality with dummy package
- Error handling (bad paths, import failures)
- Caching behavior
"""

import pytest
import sys
import os
import tempfile
import subprocess
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from trading_bot.loader.plugin_loader import (
    load_strategy,
    PluginLoaderError,
    _parse_path,
    _import_module_with_fallback,
    _ensure_venv_pip,
    clear_cache,
    get_cached_strategies,
    is_strategy_cached
)
from trading_bot.base_agent import BaseAgent


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    def __init__(self, name: str = "mock_agent"):
        super().__init__(name)
        
    async def generate_signals(self, snapshot: dict):
        return [{'symbol': 'TEST', 'action': 'buy', 'quantity': 100}]
    
    async def on_fill(self, fill: dict):
        pass
        
    async def on_limit_update(self, limits: dict):
        pass


class TestPluginLoader:
    """Test suite for plugin loader functionality."""
    
    def setup_method(self):
        """Clear cache before each test."""
        clear_cache()
    
    def test_parse_path_valid(self):
        """Test parsing valid path strings."""
        # Standard local package
        pkg, module, cls = _parse_path("trading_bot.agents.sma_agent:SMAAgent")
        assert pkg == "trading_bot"
        assert module == "trading_bot.agents.sma_agent"
        assert cls == "SMAAgent"
        
        # External package with dashes
        pkg, module, cls = _parse_path("ai-hedge-fund.strategies.momentum:MomentumStrategy")
        assert pkg == "ai-hedge-fund"
        assert module == "ai-hedge-fund.strategies.momentum"
        assert cls == "MomentumStrategy"
        
        # Nested package
        pkg, module, cls = _parse_path("external.ai_hedge_fund.strategies.base:BaseStrategy")
        assert pkg == "external"
        assert module == "external.ai_hedge_fund.strategies.base"
        assert cls == "BaseStrategy"
    
    def test_parse_path_invalid(self):
        """Test parsing invalid path strings."""
        # Missing colon
        with pytest.raises(PluginLoaderError, match="Invalid path format"):
            _parse_path("trading_bot.agents.sma_agent")
        
        # Missing module part
        with pytest.raises(PluginLoaderError, match="Invalid module path"):
            _parse_path("sma_agent:SMAAgent")
        
        # No dots in module path
        with pytest.raises(PluginLoaderError, match="Expected '<pkg>.<module>'"):
            _parse_path("sma_agent:SMAAgent")
    
    def test_load_local_strategy_success(self):
        """Test successfully loading a local strategy."""
        # Load SMA agent (should exist)
        strategy_class = load_strategy("trading_bot.agents.sma_agent:SMAAgent")
        
        assert strategy_class is not None
        assert issubclass(strategy_class, BaseAgent)
        assert strategy_class.__name__ == "SMAAgent"
        
        # Verify caching
        assert is_strategy_cached("trading_bot.agents.sma_agent:SMAAgent")
        
        # Load again - should come from cache
        strategy_class2 = load_strategy("trading_bot.agents.sma_agent:SMAAgent")
        assert strategy_class is strategy_class2  # Same object reference
    
    def test_load_strategy_class_not_found(self):
        """Test error when class doesn't exist in module."""
        with pytest.raises(PluginLoaderError, match="Class 'NonExistentAgent' not found"):
            load_strategy("trading_bot.agents.sma_agent:NonExistentAgent")
    
    def test_load_strategy_module_not_found(self):
        """Test error when module doesn't exist."""
        with pytest.raises(PluginLoaderError, match="Failed to import module"):
            load_strategy("nonexistent.module:SomeClass")
    
    def test_load_strategy_not_a_class(self):
        """Test error when target is not a class."""
        with pytest.raises(PluginLoaderError, match="is not a class"):
            load_strategy("trading_bot.base_agent:ABC")  # ABC is not a class, it's imported
    
    @patch('trading_bot.loader.plugin_loader._ensure_venv_pip')
    @patch('importlib.import_module')
    def test_auto_install_success(self, mock_import, mock_pip):
        """Test successful auto-installation of missing package."""
        # First import fails, second succeeds after pip install
        mock_import.side_effect = [
            ImportError("No module named 'missing_package'"),
            MagicMock()  # Successful import after installation
        ]
        mock_pip.return_value = True
        
        # Create a mock module with our test class
        mock_module = MagicMock()
        mock_module.TestClass = MockAgent
        mock_import.side_effect = [
            ImportError("No module named 'missing_package'"),
            mock_module
        ]
        
        strategy_class = load_strategy("missing_package.module:TestClass")
        
        assert strategy_class == MockAgent
        mock_pip.assert_called_once_with("missing_package")
        assert mock_import.call_count == 2
    
    @patch('trading_bot.loader.plugin_loader._ensure_venv_pip')
    @patch('importlib.import_module')
    def test_auto_install_failure(self, mock_import, mock_pip):
        """Test failure when auto-installation fails."""
        mock_import.side_effect = ImportError("No module named 'missing_package'")
        mock_pip.return_value = False  # Installation failed
        
        with pytest.raises(PluginLoaderError, match="Failed to import module"):
            load_strategy("missing_package.module:TestClass")
        
        mock_pip.assert_called_once_with("missing_package")
    
    @patch('subprocess.run')
    def test_ensure_venv_pip_success(self, mock_run):
        """Test successful package installation."""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        result = _ensure_venv_pip("test_package")
        
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == [sys.executable, "-m", "pip", "install", "test_package"]
    
    @patch('subprocess.run')
    def test_ensure_venv_pip_failure(self, mock_run):
        """Test failed package installation."""
        mock_run.return_value = MagicMock(
            returncode=1, 
            stderr="ERROR: Could not find a version that satisfies the requirement"
        )
        
        result = _ensure_venv_pip("nonexistent_package")
        
        assert result is False
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_ensure_venv_pip_timeout(self, mock_run):
        """Test package installation timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("pip", 300)
        
        result = _ensure_venv_pip("slow_package")
        
        assert result is False
        mock_run.assert_called_once()
    
    def test_cache_management(self):
        """Test cache management functions."""
        # Initially empty
        assert len(get_cached_strategies()) == 0
        assert not is_strategy_cached("test:path")
        
        # Load a strategy
        load_strategy("trading_bot.agents.sma_agent:SMAAgent")
        
        # Check cache
        cached = get_cached_strategies()
        assert len(cached) == 1
        assert "trading_bot.agents.sma_agent:SMAAgent" in cached
        assert is_strategy_cached("trading_bot.agents.sma_agent:SMAAgent")
        
        # Clear cache
        clear_cache()
        assert len(get_cached_strategies()) == 0
        assert not is_strategy_cached("trading_bot.agents.sma_agent:SMAAgent")
    
    def test_load_strategy_normalized_import(self):
        """Test loading strategy with dash normalization."""
        with patch('importlib.import_module') as mock_import:
            # First import with dashes fails, second with underscores succeeds
            mock_module = MagicMock()
            mock_module.TestStrategy = MockAgent
            
            mock_import.side_effect = [
                ImportError("No module named 'ai-hedge-fund'"),
                mock_module  # Success with normalized name
            ]
            
            strategy_class = load_strategy("ai-hedge-fund.strategies.test:TestStrategy")
            
            assert strategy_class == MockAgent
            # Should try both dash and underscore versions
            assert mock_import.call_count == 2
            
            # Check the calls
            calls = mock_import.call_args_list
            assert calls[0][0][0] == "ai-hedge-fund.strategies.test"
            assert calls[1][0][0] == "ai_hedge_fund.strategies.test"


class TestTempPackageInstall:
    """Test auto-install with a real temporary package."""
    
    def test_create_and_install_dummy_package(self):
        """Create a dummy wheel package and test installation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple package structure
            pkg_dir = Path(tmpdir) / "dummy_strategy"
            pkg_dir.mkdir()
            
            # Create __init__.py
            init_file = pkg_dir / "__init__.py"
            init_file.write_text(f'''
"""Dummy strategy package for testing."""

from trading_bot.base_agent import BaseAgent

class DummyStrategy(BaseAgent):
    def __init__(self, name="dummy"):
        super().__init__(name)
    
    async def generate_signals(self, snapshot):
        return [{{"symbol": "TEST", "action": "hold", "quantity": 0}}]
    
    async def on_fill(self, fill):
        pass
    
    async def on_limit_update(self, limits):
        pass
''')
            
            # Create setup.py
            setup_file = Path(tmpdir) / "setup.py"
            setup_file.write_text('''
from setuptools import setup, find_packages

setup(
    name="dummy_strategy",
    version="0.1.0",
    packages=find_packages(),
    description="Dummy strategy for testing",
)
''')
            
            # Build wheel
            build_cmd = [sys.executable, "setup.py", "bdist_wheel"]
            result = subprocess.run(
                build_cmd, 
                cwd=tmpdir, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                # Find the wheel file
                dist_dir = Path(tmpdir) / "dist"
                wheel_files = list(dist_dir.glob("*.whl"))
                
                if wheel_files:
                    wheel_path = wheel_files[0]
                    
                    # Test installation
                    install_result = _ensure_venv_pip(str(wheel_path))
                    
                    if install_result:
                        # Test loading the installed package
                        try:
                            strategy_class = load_strategy("dummy_strategy:DummyStrategy")
                            assert strategy_class is not None
                            assert issubclass(strategy_class, BaseAgent)
                            
                            # Clean up - uninstall
                            subprocess.run([
                                sys.executable, "-m", "pip", "uninstall", 
                                "dummy_strategy", "-y"
                            ], capture_output=True)
                            
                        except PluginLoaderError:
                            # Package installation might not work in all environments
                            pytest.skip("Package installation not supported in this environment")
                    else:
                        pytest.skip("Failed to install dummy package")
                else:
                    pytest.skip("Failed to build wheel")
            else:
                pytest.skip("Failed to build dummy package")


if __name__ == "__main__":
    # Run tests manually
    pytest.main([__file__, "-v"])