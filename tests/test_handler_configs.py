"""Tests for various handler configurations."""

from pydantic_settings_logging import (
    LoggingSettings,
    RotatingFileHandlerConfig,
    TimedRotatingFileHandlerConfig,
)


def test_rotating_file_handler():
    """Test strongly typed RotatingFileHandler configuration."""
    settings = LoggingSettings(
        handlers={
            "rotating": RotatingFileHandlerConfig(
                filename="test.log",
                maxBytes=1048576,
                backupCount=5,
                formatter="simple"
            )
        }
    )
    
    config_dict = settings.model_dump()
    handler = config_dict["handlers"]["rotating"]
    
    assert handler["class"] == "logging.handlers.RotatingFileHandler"
    assert handler["maxBytes"] == 1048576
    assert handler["backupCount"] == 5


def test_timed_rotating_file_handler():
    """Test strongly typed TimedRotatingFileHandler configuration."""
    settings = LoggingSettings(
        handlers={
            "timed": TimedRotatingFileHandlerConfig(
                filename="app.log",
                when="midnight",
                interval=1,
                backupCount=30
            )
        }
    )
    
    config_dict = settings.model_dump()
    handler = config_dict["handlers"]["timed"]
    
    assert handler["class"] == "logging.handlers.TimedRotatingFileHandler"
    assert handler["when"] == "midnight"
    assert handler["interval"] == 1
    assert handler["backupCount"] == 30


def test_smtp_handler():
    """Test SMTPHandler configuration."""
    settings = LoggingSettings(
        handlers={
            "email": {
                "class": "logging.handlers.SMTPHandler",
                "mailhost": "smtp.example.com",
                "fromaddr": "app@example.com",
                "toaddrs": ["admin@example.com", "ops@example.com"],
                "subject": "Application Error",
                "level": "ERROR"
            }
        }
    )
    
    config_dict = settings.model_dump()
    handler = config_dict["handlers"]["email"]
    
    assert handler["class"] == "logging.handlers.SMTPHandler"
    assert handler["mailhost"] == "smtp.example.com"
    assert handler["toaddrs"] == ["admin@example.com", "ops@example.com"]


def test_custom_handler():
    """Test custom handler configuration."""
    settings = LoggingSettings(
        handlers={
            "custom": {
                "class": "myapp.logging.CustomHandler",
                "custom_param": "value",
                "another_param": 42
            }
        }
    )
    
    config_dict = settings.model_dump()
    handler = config_dict["handlers"]["custom"]
    
    assert handler["class"] == "myapp.logging.CustomHandler"
    assert handler["custom_param"] == "value"
    assert handler["another_param"] == 42
