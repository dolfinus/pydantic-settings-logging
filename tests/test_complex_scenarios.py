"""Tests for complex real-world configuration scenarios."""

from pydantic_settings_logging import LoggingSettings


def test_multi_logger_configuration():
    """Test configuration with multiple loggers."""
    settings = LoggingSettings(
        formatters={
            "simple": {"format": "%(levelname)s: %(message)s"},
            "detailed": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
        },
        handlers={
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "simple"
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "app.log",
                "formatter": "detailed"
            }
        },
        loggers={
            "myapp": {
                "level": "DEBUG",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "myapp.database": {
                "level": "WARNING",
                "handlers": ["file"]
            },
            "third_party": {
                "level": "ERROR",
                "handlers": ["console"]
            }
        },
        root={
            "level": "WARNING",
            "handlers": ["console"]
        }
    )
    
    config_dict = settings.model_dump()
    
    assert len(config_dict["loggers"]) == 3
    assert config_dict["loggers"]["myapp"]["level"] == "DEBUG"
    assert config_dict["loggers"]["myapp"]["propagate"] is False
    assert config_dict["loggers"]["myapp.database"]["level"] == "WARNING"


def test_filters_configuration():
    """Test configuration with filters."""
    settings = LoggingSettings(
        filters={
            "myfilter": {
                "name": "myapp.specific"
            },
        },
        handlers={
            "filtered": {
                "class": "logging.StreamHandler",
                "filters": ["myfilter"]
            }
        }
    )
    
    config_dict = settings.model_dump()

    assert "myfilter" in config_dict["filters"]
    assert config_dict["filters"]["myfilter"]["name"] == "myapp.specific"
    assert config_dict["handlers"]["filtered"]["filters"] == ["myfilter"]


def test_callable_configuration():
    """Test configuration with filters."""
    settings = LoggingSettings(
        filters={
            "myfilter": {
                "()": "myapp.filter",
                "arg1": "val1",
                ".": {
                    "attr1": "val11",
                },
            },
        },
        formatters={
            "myformatter": {
                "()": "myapp.formatter",
                "arg2": "val2",
                ".": {
                    "attr2": "val22",
                },
            },
        },
        handlers={
            "myhandler": {
                "()": "myapp.handler",
                "arg3": "val3",
                ".": {
                    "attr3": "val33",
                },
            }
        }
    )
    
    config_dict = settings.model_dump()

    assert "myfilter" in config_dict["filters"]
    assert config_dict["filters"]["myfilter"]["()"] == "myapp.filter"
    assert config_dict["filters"]["myfilter"]["arg1"] == "val1"
    assert config_dict["filters"]["myfilter"]["."] == {"attr1": "val11"}

    assert "myformatter" in config_dict["formatters"]
    assert config_dict["formatters"]["myformatter"]["()"] == "myapp.formatter"
    assert config_dict["formatters"]["myformatter"]["arg2"] == "val2"
    assert config_dict["formatters"]["myformatter"]["."] == {"attr2": "val22"}

    assert "myhandler" in config_dict["handlers"]
    assert config_dict["handlers"]["myhandler"]["()"] == "myapp.handler"
    assert config_dict["handlers"]["myhandler"]["arg3"] == "val3"
    assert config_dict["handlers"]["myhandler"]["."] == {"attr3": "val33"}
