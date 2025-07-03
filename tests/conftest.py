"""Shared pytest fixtures for pydantic-settings-logging tests."""

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def tmp_logging_dir():
    """Create a temporary directory for logging configuration files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def clean_environment(monkeypatch):
    """Clean environment variables before and after tests."""
    # Store original env vars that start with LOGGING_
    original_vars = {}
    for key in list(os.environ.keys()):
        if key.startswith("LOGGING_"):
            original_vars[key] = os.environ[key]
            monkeypatch.delenv(key)
    
    yield monkeypatch
    
    # Restore original env vars
    for key in list(os.environ.keys()):
        if key.startswith("LOGGING_"):
            monkeypatch.delenv(key, raising=False)
    
    for key, value in original_vars.items():
        monkeypatch.setenv(key, value)


@contextmanager
def change_directory(path):
    """Context manager to temporarily change working directory."""
    original_cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_cwd)


@pytest.fixture
def sample_json_config():
    """Standard JSON logging configuration."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "detailed",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }


@pytest.fixture
def sample_toml_config():
    """Standard TOML logging configuration."""
    return """version = 1
disable_existing_loggers = false

[formatters.detailed]
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

[handlers.console]
class = "logging.StreamHandler"
level = "INFO"
formatter = "detailed"
stream = "ext://sys.stdout"

[root]
level = "INFO"
handlers = ["console"]
"""


@pytest.fixture
def sample_ini_config():
    """Standard INI logging configuration."""
    return """[loggers]
keys=root

[handlers]
keys=consoleHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[handler_consoleHandler]
class=logging.StreamHandler
level=DEBUG
formatter=simpleFormatter

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
"""


@pytest.fixture
def multilogger_ini_config():
    """Complex INI configuration with multiple loggers."""
    return """[loggers]
keys=root,myapp,myapp.database

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=detailed

[logger_root]
level=WARNING
handlers=consoleHandler

[logger_myapp]
level=DEBUG
handlers=consoleHandler,fileHandler
propagate=0
qualname=myapp

[logger_myapp.database]
level=INFO
handlers=fileHandler
propagate=1
qualname=myapp.database

[handler_consoleHandler]
class=logging.StreamHandler
level=INFO
formatter=detailed

[handler_fileHandler]
class=logging.FileHandler
level=DEBUG
formatter=detailed
filename=app.log

[formatter_detailed]
format=%(asctime)s [%(levelname)s] %(name)s: %(message)s
datefmt=%Y-%m-%d %H:%M:%S
"""


@pytest.fixture
def config_file_factory(tmp_logging_dir):
    """Factory for creating configuration files."""
    def _create_config_file(filename: str, content: Any, file_type: str = "json"):
        """Create a configuration file in the temporary directory.
        
        Args:
            filename: Name of the file to create
            content: Content to write (dict for JSON, string for others)
            file_type: Type of file ("json", "toml", "ini")
        """
        file_path = tmp_logging_dir / filename
        
        if file_type == "json":
            with open(file_path, "w") as f:
                json.dump(content, f)
        else:
            with open(file_path, "w") as f:
                f.write(content)
        
        return file_path
    
    return _create_config_file


@pytest.fixture
def logger_settings_factory():
    """Factory for creating LoggingSettings instances with various configurations."""
    from pydantic_settings_logging import LoggingSettings
    
    def _create_settings(**kwargs):
        """Create LoggingSettings instance with given parameters."""
        return LoggingSettings(**kwargs)
    
    return _create_settings
