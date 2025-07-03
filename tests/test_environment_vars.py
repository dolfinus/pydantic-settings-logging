"""Tests for environment variable configuration."""

from pydantic_settings_logging import LoggingSettings


def test_env_var_override(clean_environment):
    """Test that environment variables override file configuration."""
    clean_environment.setenv("LOGGING_ROOT__LEVEL", "ERROR")
    clean_environment.setenv("LOGGING_DISABLE_EXISTING_LOGGERS", "false")
    clean_environment.setenv("LOGGING_FORMATTERS__ENV__FORMAT", "[ENV] %(levelname)s: %(message)s")
    
    settings = LoggingSettings()
    
    assert settings.root.level == "ERROR"
    assert settings.disable_existing_loggers is False
    assert "env" in settings.formatters
    assert settings.formatters["env"].format == "[ENV] %(levelname)s: %(message)s"


def test_nested_env_vars(clean_environment):
    """Test nested environment variable configuration."""
    clean_environment.setenv("LOGGING_HANDLERS__CONSOLE__CLASS", "logging.StreamHandler")
    clean_environment.setenv("LOGGING_HANDLERS__CONSOLE__LEVEL", "WARNING")
    clean_environment.setenv("LOGGING_HANDLERS__CONSOLE__STREAM", "ext://sys.stderr")
    
    settings = LoggingSettings()
    config_dict = settings.model_dump()
    
    assert "console" in config_dict["handlers"]
    assert config_dict["handlers"]["console"]["class"] == "logging.StreamHandler"
    assert config_dict["handlers"]["console"]["level"] == "WARNING"
    assert config_dict["handlers"]["console"]["stream"] == "ext://sys.stderr"
