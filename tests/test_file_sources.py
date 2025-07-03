"""Tests for file-based configuration sources."""

from conftest import change_directory
from pydantic_settings_logging import LoggingSettings


def test_json_configuration(tmp_logging_dir, sample_json_config, config_file_factory):
    """Test loading from JSON file."""
    config_file_factory("logging.json", sample_json_config, "json")
    
    with change_directory(tmp_logging_dir):
        settings = LoggingSettings()
        config_dict = settings.model_dump()
        
        assert "detailed" in config_dict["formatters"]
        assert config_dict["formatters"]["detailed"]["format"] == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert "console" in config_dict["handlers"]
        assert config_dict["handlers"]["console"]["class"] == "logging.StreamHandler"


def test_toml_configuration(tmp_logging_dir, sample_toml_config, config_file_factory):
    """Test loading from TOML file."""
    config_file_factory("logging.toml", sample_toml_config, "toml")
    
    with change_directory(tmp_logging_dir):
        settings = LoggingSettings()
        config_dict = settings.model_dump()
        
        assert "detailed" in config_dict["formatters"]
        assert config_dict["formatters"]["detailed"]["format"] == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def test_pyproject_toml_configuration(tmp_logging_dir, config_file_factory):
    """Test loading from pyproject.toml."""
    pyproject_content = """
[tool.logging]
version = 1

[tool.logging.formatters.pyproject]
format = "[PYPROJECT] %(message)s"

[tool.logging.handlers.console]
class = "logging.StreamHandler"
formatter = "pyproject"

[tool.logging.root]
handlers = ["console"]
"""
    config_file_factory("pyproject.toml", pyproject_content, "toml")
    
    with change_directory(tmp_logging_dir):
        settings = LoggingSettings()
        config_dict = settings.model_dump()
        
        assert "pyproject" in config_dict["formatters"]
        assert config_dict["formatters"]["pyproject"]["format"] == "[PYPROJECT] %(message)s"


def test_ini_configuration(tmp_logging_dir, sample_ini_config, config_file_factory):
    """Test loading from INI file."""
    config_file_factory("logging.ini", sample_ini_config, "ini")
    
    with change_directory(tmp_logging_dir):
        settings = LoggingSettings()
        config_dict = settings.model_dump()
        
        assert "simpleFormatter" in config_dict["formatters"]
        assert config_dict["formatters"]["simpleFormatter"]["format"] == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert "consoleHandler" in config_dict["handlers"]
        assert config_dict["handlers"]["consoleHandler"]["class"] == "logging.StreamHandler"
        assert config_dict["root"]["level"] == "INFO"
        assert config_dict["root"]["handlers"] == ["consoleHandler"]
