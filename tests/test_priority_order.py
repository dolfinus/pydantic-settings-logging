"""Tests for configuration source priority order."""

import json

from conftest import change_directory
from pydantic_settings_logging import LoggingSettings


def test_file_priority(tmp_logging_dir, config_file_factory):
    """Test that files override each other in correct order."""
    # Create TOML file (lower priority)
    config_file_factory("logging.toml", '[root]\nlevel = "DEBUG"\n', "toml")
    
    # Create JSON file (higher priority)
    json_config = {"version": 1, "root": {"level": "INFO"}}
    config_file_factory("logging.json", json_config, "json")
    
    with change_directory(tmp_logging_dir):
        settings = LoggingSettings()
        assert settings.root.level == "INFO"  # JSON wins over TOML


def test_ini_priority_order(tmp_logging_dir, config_file_factory):
    """Test that INI files have correct priority in the configuration chain."""
    # Create INI file (lower priority than JSON and TOML)
    ini_content = """[loggers]
keys=root

[handlers]
keys=consoleHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=ERROR
handlers=consoleHandler

[handler_consoleHandler]
class=logging.StreamHandler
level=DEBUG
formatter=simpleFormatter

[formatter_simpleFormatter]
format=INI: %(message)s
"""
    config_file_factory("logging.ini", ini_content, "ini")
    
    # Create TOML file (higher priority than INI)
    toml_content = '[root]\nlevel = "WARNING"\n[formatters.simpleFormatter]\nformat = "TOML: %(message)s"\n'
    config_file_factory("logging.toml", toml_content, "toml")
    
    with change_directory(tmp_logging_dir):
        settings = LoggingSettings()
        config_dict = settings.model_dump()
        
        # TOML should override INI
        assert config_dict["root"]["level"] == "WARNING"  # TOML wins
        assert config_dict["formatters"]["simpleFormatter"]["format"] == "TOML: %(message)s"  # TOML wins


def test_env_overrides_files(tmp_logging_dir, config_file_factory, clean_environment):
    """Test that environment variables override file configurations."""
    # Create JSON file
    json_config = {"version": 1, "disable_existing_loggers": True}
    config_file_factory("logging.json", json_config, "json")
    
    # Set environment variable to override
    clean_environment.setenv("LOGGING_DISABLE_EXISTING_LOGGERS", "false")
    
    with change_directory(tmp_logging_dir):
        settings = LoggingSettings()
        assert settings.disable_existing_loggers is False  # Environment wins


def test_init_overrides_everything(tmp_logging_dir, config_file_factory, clean_environment):
    """Test that direct initialization overrides all other sources."""
    # Create JSON file
    json_config = {"version": 1, "disable_existing_loggers": True}
    config_file_factory("logging.json", json_config, "json")
    
    # Set environment variable
    clean_environment.setenv("LOGGING_DISABLE_EXISTING_LOGGERS", "true")
    
    with change_directory(tmp_logging_dir):
        # Direct initialization should override everything
        settings = LoggingSettings(disable_existing_loggers=False)
        assert settings.disable_existing_loggers is False  # Init wins
