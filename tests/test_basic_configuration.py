"""Tests for basic LoggingSettings configuration functionality."""

import logging.config

from pydantic_settings_logging import (
    LoggingSettings,
    FormatterConfig,
    StreamHandlerConfig,
    RootLoggerConfig,
)


def test_minimal_configuration():
    """Test minimal configuration with defaults."""
    settings = LoggingSettings()
    config_dict = settings.model_dump()
    
    assert config_dict["version"] == 1
    assert "disable_existing_loggers" in config_dict
    assert config_dict["incremental"] is False


def test_programmatic_configuration():
    """Test strongly typed programmatic configuration."""
    settings = LoggingSettings(
        formatters={
            "simple": FormatterConfig(
                format="%(levelname)s: %(message)s"
            )
        },
        handlers={
            "console": StreamHandlerConfig(
                level="INFO",
                formatter="simple",
                stream="ext://sys.stdout"
            )
        },
        root=RootLoggerConfig(
            level="INFO",
            handlers=["console"]
        )
    )
    
    config_dict = settings.model_dump()
    
    assert "simple" in config_dict["formatters"]
    assert config_dict["formatters"]["simple"]["format"] == "%(levelname)s: %(message)s"
    assert "console" in config_dict["handlers"]
    assert config_dict["handlers"]["console"]["class"] == "logging.StreamHandler"
    assert config_dict["root"]["level"] == "INFO"
    assert config_dict["root"]["handlers"] == ["console"]


def test_dictconfig_compatibility():
    """Test that strongly typed output is compatible with logging.dictConfig."""
    settings = LoggingSettings(
        handlers={
            "console": StreamHandlerConfig(
                level="DEBUG"
            )
        },
        root=RootLoggerConfig(
            handlers=["console"]
        )
    )
    
    config_dict = settings.model_dump()
    
    # This should not raise an exception
    logging.config.dictConfig(config_dict)
    
    # Test that logging works
    logger = logging.getLogger("test")
    logger.debug("Test message")  # Should not raise
