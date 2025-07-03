"""Tests for INI format compatibility and edge cases."""

from conftest import change_directory
from pydantic_settings_logging import LoggingSettings


def test_complex_ini_configuration(tmp_logging_dir, multilogger_ini_config, config_file_factory):
    """Test loading complex INI configuration with multiple loggers."""
    config_file_factory("logging.ini", multilogger_ini_config, "ini")
    
    with change_directory(tmp_logging_dir):
        settings = LoggingSettings()
        config_dict = settings.model_dump()
        
        # Check formatters
        assert "detailed" in config_dict["formatters"]
        assert config_dict["formatters"]["detailed"]["format"] == "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        assert config_dict["formatters"]["detailed"]["datefmt"] == "%Y-%m-%d %H:%M:%S"
        
        # Check handlers
        assert "consoleHandler" in config_dict["handlers"]
        assert "fileHandler" in config_dict["handlers"]
        assert config_dict["handlers"]["fileHandler"]["filename"] == "app.log"
        
        # Check loggers
        assert "myapp" in config_dict["loggers"]
        assert "myapp.database" in config_dict["loggers"]
        assert config_dict["loggers"]["myapp"]["level"] == "DEBUG"
        assert config_dict["loggers"]["myapp"]["propagate"] is False
        assert config_dict["loggers"]["myapp.database"]["level"] == "INFO"
        assert config_dict["loggers"]["myapp.database"]["propagate"] is True
        
        # Check root logger
        assert config_dict["root"]["level"] == "WARNING"
        assert config_dict["root"]["handlers"] == ["consoleHandler"]


def test_ini_edge_cases(tmp_logging_dir, config_file_factory):
    """Test INI configuration edge cases and special syntax."""
    ini_content = """[loggers]
keys=root

[handlers]
keys=rotatingHandler

[formatters]
keys=detailedFormatter

[logger_root]
level=DEBUG
handlers=rotatingHandler

[handler_rotatingHandler]
class=logging.handlers.RotatingFileHandler
level=INFO
formatter=detailedFormatter
filename=rotate.log
maxBytes=1048576
backupCount=3
mode=a
encoding=utf-8

[formatter_detailedFormatter]
format=%(asctime)s [%(process)d] %(name)s %(levelname)s: %(message)s
datefmt=%Y-%m-%d %H:%M:%S
validate=true
"""
    config_file_factory("logging.ini", ini_content, "ini")
    
    with change_directory(tmp_logging_dir):
        settings = LoggingSettings()
        config_dict = settings.model_dump()
        
        # Check handler details
        handler = config_dict["handlers"]["rotatingHandler"]
        assert handler["class"] == "logging.handlers.RotatingFileHandler"
        assert handler["maxBytes"] == 1048576
        assert handler["backupCount"] == 3
        assert handler["mode"] == "a"
        assert handler["encoding"] == "utf-8"
        
        # Check formatter with validation
        formatter = config_dict["formatters"]["detailedFormatter"]
        assert formatter["format"] == "%(asctime)s [%(process)d] %(name)s %(levelname)s: %(message)s"
        assert formatter["datefmt"] == "%Y-%m-%d %H:%M:%S"
        assert formatter["validate"] is True
