# pydantic-settings-logging

[![PyPI version](https://badge.fury.io/py/pydantic-settings-logging.svg)](https://badge.fury.io/py/pydantic-settings-logging)
[![Python versions](https://img.shields.io/pypi/pyversions/pydantic-settings-logging.svg)](https://pypi.org/project/pydantic-settings-logging/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A `pydantic` based library for configuring Python's `logging` module.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [Basic Usage](#basic-usage)
  - [Strongly Typed Configuration](#strongly-typed-configuration)
- [Configuration Sources](#configuration-sources)
  - [Environment Variables](#environment-variables)
  - [TOML Configuration](#toml-configuration-loggingtoml)
  - [JSON Configuration](#json-configuration-loggingjson)
  - [pyproject.toml Configuration](#pyprojecttoml-configuration)
- [Common Patterns](#common-patterns)
  - [Development vs Production](#development-vs-production)
  - [Multiple Handlers with Type Safety](#multiple-handlers-with-type-safety)
  - [Email Notifications for Critical Errors](#email-notifications-for-critical-errors)
  - [Time-Based Log Rotation](#time-based-log-rotation)
- [Advanced Usage](#advanced-usage)
  - [Custom Configuration Sources](#custom-configuration-sources)
  - [Extending with Custom Handlers](#extending-with-custom-handlers)
- [Supported Handlers](#supported-handlers)
- [Contributing](#contributing)
- [License](#license)

## Features

- **🔒 Full type safety**: Leverage `pydantic`'s validation for all logging configurations
- **📁 Multiple configuration sources**: JSON, TOML files, environment variables, and `pyproject.toml`
- **⚡ Automatic source priority**: Environment variables override files, with configurable precedence
- **🎯 Complete logging coverage**: Support for all standard Python logging handlers, formatters, and filters
- **🔧 Easy integration**: Simply call `model_dump()` to get a dict ready for `logging.config.dictConfig()`
- **💻 IDE support**: Full autocompletion, type hints, and validation in your editor

## Installation

```bash
pip install pydantic-settings-logging
```

## Quick Start

### Basic Usage

```python
import logging.config
from pydantic_settings_logging import LoggingSettings

# Load configuration from all available sources
settings = LoggingSettings()

# Apply configuration to Python's logging system
logging.config.dictConfig(settings.model_dump())

# Start logging
logger = logging.getLogger(__name__)
logger.info("Configuration loaded successfully!")
```

### Strongly Typed Configuration

```python
import logging.config
from pydantic_settings_logging import (
    LoggingSettings, 
    FormatterConfig, 
    StreamHandlerConfig,
    RootLoggerConfig
)

# Strongly typed configuration with full IDE support and validation
settings = LoggingSettings(
    formatters={
        "detailed": FormatterConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ),
        "simple": FormatterConfig(
            format="%(levelname)s: %(message)s"
        )
    },
    handlers={
        "console": StreamHandlerConfig(
            level="INFO",
            formatter="detailed",
            stream="ext://sys.stdout"
        )
    },
    root=RootLoggerConfig(
        level="INFO",
        handlers=["console"]
    )
)

# Your IDE will catch typos, missing formatters, invalid levels, etc.
logging.config.dictConfig(settings.model_dump())
```

## Configuration Sources

The library loads configuration from multiple sources in the following
priority:

1. Arguments passed to the `LoggingSettings` constructor
2. Environment variables (with `LOGGING_` prefix)
3. `logging.json` JSON configuration file  
4. `logging.toml` TOML configuration file
5. `logging.ini` INI configuration file (`logging.config.fileConfig` format)
6. `pyproject.toml` (in `[tool.logging]` section)

### Environment Variables

Use the `LOGGING_` prefix and double underscores for nested values:

```bash
export LOGGING_ROOT__LEVEL=DEBUG
export LOGGING_HANDLERS__CONSOLE__LEVEL=INFO
export LOGGING_FORMATTERS__SIMPLE__FORMAT="%(levelname)s: %(message)s"
```

### JSON Configuration (logging.json)

```json
{
  "version": 1,
  "disable_existing_loggers": false,
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
```

### TOML Configuration (logging.toml)

```toml
version = 1
disable_existing_loggers = false

[formatters.detailed]
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

[handlers.console]
class = "logging.StreamHandler"
level = "INFO"
formatter = "detailed"
stream = "ext://sys.stdout"

[handlers.file]
class = "logging.handlers.RotatingFileHandler"
level = "DEBUG"
formatter = "detailed"
filename = "app.log"
maxBytes = 10485760
backupCount = 3

[loggers.myapp]
level = "DEBUG"
handlers = ["console", "file"]

[root]
level = "INFO"
handlers = ["console"]
```

### pyproject.toml Configuration

```toml
[tool.logging]
version = 1
disable_existing_loggers = false

[tool.logging.formatters.detailed]
format = "%(asctime)s - %(levelname)s - %(message)s"

[tool.logging.handlers.console]
class = "logging.StreamHandler"
level = "INFO"
formatter = "detailed"

[tool.logging.root]
level = "INFO"
handlers = ["console"]
```

### INI Configuration (logging.ini)

Compatible with Python's standard `logging.config.fileConfig()` format:

```ini
[loggers]
keys=root,myapp

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=detailed,simple

[logger_root]
level=WARNING
handlers=consoleHandler

[logger_myapp]
level=DEBUG
handlers=consoleHandler,fileHandler
propagate=0
qualname=myapp

[handler_consoleHandler]
class=logging.StreamHandler
level=INFO
formatter=detailed
stream=ext://sys.stdout

[handler_fileHandler]
class=logging.handlers.RotatingFileHandler
level=DEBUG
formatter=detailed
filename=app.log
maxBytes=10485760
backupCount=3

[formatter_detailed]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S

[formatter_simple]
format=%(levelname)s: %(message)s
```

This provides a **smooth migration path** from existing `logging.config.fileConfig()` configurations while gaining the benefits of type safety and validation.

## Common Patterns

### Development vs Production

Use environment variables to override file-based configuration:

```bash
# Base configuration in logging.toml
# Override for development
export LOGGING_HANDLERS__CONSOLE__LEVEL=DEBUG

# Override for production  
export LOGGING_HANDLERS__CONSOLE__LEVEL=WARNING
```

### Multiple Handlers with Type Safety

Configure multiple handlers with full type checking:

```python
from pydantic_settings_logging import (
    LoggingSettings,
    StreamHandlerConfig, 
    RotatingFileHandlerConfig,
    FileHandlerConfig,
    RootLoggerConfig
)

settings = LoggingSettings(
    handlers={
        "console": StreamHandlerConfig(
            level="WARNING",
            stream="ext://sys.stderr"
        ),
        "debug_file": RotatingFileHandlerConfig(
            level="DEBUG",
            filename="debug.log",
            maxBytes=10485760,
            backupCount=5
        ),
        "error_file": FileHandlerConfig(
            level="ERROR",
            filename="errors.log"
        )
    },
    root=RootLoggerConfig(
        handlers=["console", "debug_file", "error_file"]
    )
)
```

### Email Notifications for Critical Errors

```python
from pydantic_settings_logging import (
    LoggingSettings,
    SMTPHandlerConfig,
    LoggerConfig
)

settings = LoggingSettings(
    handlers={
        "email_alerts": SMTPHandlerConfig(
            level="ERROR",
            mailhost="smtp.example.com",
            fromaddr="app@example.com", 
            toaddrs=["admin@example.com"],
            subject="Critical Application Error"
        )
    },
    loggers={
        "myapp.critical": LoggerConfig(
            handlers=["email_alerts"],
            level="ERROR"
        )
    }
)
```

### Time-Based Log Rotation

```python
from pydantic_settings_logging import (
    LoggingSettings,
    TimedRotatingFileHandlerConfig
)

settings = LoggingSettings(
    handlers={
        "daily_logs": TimedRotatingFileHandlerConfig(
            filename="app.log",
            when="midnight",
            interval=1,
            backupCount=30,
            formatter="detailed"
        )
    }
)
```

## Advanced Usage

### Custom Configuration Sources

Specify custom file paths and environment prefix:

```python
from pydantic_settings_logging import LoggingSettings

# Load from custom paths with custom environment prefix
settings = LoggingSettings(
    env_prefix="MYAPP_LOGGING_",
    toml_file="config/logging.toml", 
    json_file="config/logging.json",
    ini_file="config/logging.ini"
)

logging.config.dictConfig(settings.model_dump())
```

### Extending with Custom Handlers

The library supports custom handlers with additional parameters:

```python
from pydantic_settings_logging import LoggingSettings, BaseHandlerConfig

# Custom handler with extra parameters
class CustomHandlerConfig(BaseHandlerConfig):
    custom_param: str
    retry_count: int = 3

settings = LoggingSettings(
    handlers={
        "custom": CustomHandlerConfig(
            class_="myapp.handlers.CustomHandler",
            level="INFO",
            custom_param="value",
            retry_count=5
        )
    }
)
```

## Supported Handlers

The library includes strongly typed support for all standard Python logging handlers:

- **StreamHandler**: Console output
- **FileHandler**: Basic file output  
- **RotatingFileHandler**: Size-based rotation
- **TimedRotatingFileHandler**: Time-based rotation
- **SocketHandler**: TCP socket output
- **DatagramHandler**: UDP socket output
- **SysLogHandler**: System log daemon
- **NTEventLogHandler**: Windows event log
- **SMTPHandler**: Email notifications
- **MemoryHandler**: Buffering handler
- **HTTPHandler**: HTTP POST requests
- **QueueHandler**: Asynchronous logging
- **QueueListener**: Asynchronous log processing

Each handler has its own strongly typed configuration class with full validation.

## Migration from Native Logging

### From `logging.config.fileConfig()`

If you're currently using INI-style configuration files:

**Before** (native logging):

```python
import logging.config
logging.config.fileConfig('logging.ini')
```

**After** (pydantic-settings-logging):

```python
import logging.config
from pydantic_settings_logging import LoggingSettings

# Your existing logging.ini file works as-is!
settings = LoggingSettings()  # Automatically loads logging.ini
logging.config.dictConfig(settings.model_dump())
```

### From `logging.config.dictConfig()`

**Before** (raw dictionaries):

```python
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

**After** (strongly typed):

```python
import logging.config
from pydantic_settings_logging import (
    LoggingSettings, FormatterConfig, StreamHandlerConfig, RootLoggerConfig
)

settings = LoggingSettings(
    formatters={
        "detailed": FormatterConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    },
    handlers={
        "console": StreamHandlerConfig(
            level="INFO",
            formatter="detailed"
        )
    },
    root=RootLoggerConfig(
        level="INFO",
        handlers=["console"]
    )
)

logging.config.dictConfig(settings.model_dump())
```

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
