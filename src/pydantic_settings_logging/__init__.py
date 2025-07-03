"""
pydantic-settings-logging: Pydantic models for Python logging configuration.

This package provides Pydantic models that integrate with pydantic-settings
to allow easy configuration of Python's logging module from multiple sources
including environment variables, TOML, JSON, and pyproject.toml files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, Field, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import json
from configparser import ConfigParser

__version__ = "0.1.0a1"
__all__ = [
    "LoggingSettings",
    "FormatterConfig", 
    "FilterConfig",
    "StreamHandlerConfig",
    "FileHandlerConfig",
    "RotatingFileHandlerConfig",
    "TimedRotatingFileHandlerConfig",
    "LoggerConfig",
    "RootLoggerConfig",
]


# Formatter Models
class FormatterConfig(BaseModel):
    """Configuration for a logging formatter."""
    
    format: str | None = Field(
        default="%(levelname)s:%(name)s:%(message)s",
        description="Format string for log messages"
    )
    datefmt: str | None = Field(
        default=None,
        description="Format string for date/time"
    )
    style: Literal["%", "{", "$"] = Field(
        default="%",
        description="Format style"
    )
    validate_format: bool | None = Field(
        default=None,
        alias="validate",
        description="Validate the format string"
    )
    defaults: dict[str, Any] | None = Field(
        default=None,
        description="Default values for custom fields"
    )
    class_: str | None = Field(
        default=None,
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class",
        description="Custom formatter class"
    )


# Filter Models
class FilterConfig(BaseModel):
    """Configuration for a logging filter."""
    
    name: str | None = Field(
        default="",
        description="Logger name to filter"
    )
    class_: str | None = Field(
        default=None,
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class",
        description="Custom filter class"
    )


# Handler Models
class BaseHandlerConfig(BaseModel):
    """Base configuration for all handlers."""
    
    model_config = {"extra": "allow"}
    
    class_: str = Field(
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class",
        description="Handler class"
    )
    level: str | None = Field(
        default=None,
        description="Logging level"
    )
    formatter: str | None = Field(
        default=None,
        description="Formatter ID"
    )
    filters: list[str] | None = Field(
        default=None,
        description="List of filter IDs"
    )


class StreamHandlerConfig(BaseHandlerConfig):
    """Configuration for StreamHandler."""
    
    class_: Literal["logging.StreamHandler"] = Field(
        default="logging.StreamHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    stream: str | None = Field(
        default=None,
        description="Stream to write to (e.g., 'ext://sys.stdout')"
    )


class FileHandlerConfig(BaseHandlerConfig):
    """Configuration for FileHandler."""
    
    class_: Literal["logging.FileHandler"] = Field(
        default="logging.FileHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    filename: str = Field(
        description="Path to log file"
    )
    mode: str = Field(
        default="a",
        description="File opening mode"
    )
    encoding: str | None = Field(
        default=None,
        description="File encoding"
    )
    delay: bool = Field(
        default=False,
        description="Delay file opening until first write"
    )
    errors: str | None = Field(
        default=None,
        description="Error handling scheme"
    )


class WatchedFileHandlerConfig(FileHandlerConfig):
    """Configuration for WatchedFileHandler."""
    
    class_: Literal["logging.handlers.WatchedFileHandler"] = Field(
        default="logging.handlers.WatchedFileHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )


class RotatingFileHandlerConfig(FileHandlerConfig):
    """Configuration for RotatingFileHandler."""
    
    class_: Literal["logging.handlers.RotatingFileHandler"] = Field(
        default="logging.handlers.RotatingFileHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    maxBytes: int = Field(
        default=0,
        description="Maximum file size in bytes"
    )
    backupCount: int = Field(
        default=0,
        description="Number of backup files to keep"
    )


class TimedRotatingFileHandlerConfig(FileHandlerConfig):
    """Configuration for TimedRotatingFileHandler."""
    
    class_: Literal["logging.handlers.TimedRotatingFileHandler"] = Field(
        default="logging.handlers.TimedRotatingFileHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    when: Literal["S", "M", "H", "D", "W0", "W1", "W2", "W3", "W4", "W5", "W6", "midnight"] = Field(
        default="h",
        description="Type of time interval"
    )
    interval: int = Field(
        default=1,
        description="Rotation interval"
    )
    backupCount: int = Field(
        default=0,
        description="Number of backup files to keep"
    )
    utc: bool = Field(
        default=False,
        description="Use UTC time"
    )
    atTime: str | None = Field(
        default=None,
        description="Time of day for rotation"
    )


class SocketHandlerConfig(BaseHandlerConfig):
    """Configuration for SocketHandler."""
    
    class_: Literal["logging.handlers.SocketHandler"] = Field(
        default="logging.handlers.SocketHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    host: str = Field(
        description="Hostname"
    )
    port: int = Field(
        description="Port number"
    )


class DatagramHandlerConfig(BaseHandlerConfig):
    """Configuration for DatagramHandler."""
    
    class_: Literal["logging.handlers.DatagramHandler"] = Field(
        default="logging.handlers.DatagramHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    host: str = Field(
        description="Hostname"
    )
    port: int = Field(
        description="Port number"
    )


class SysLogHandlerConfig(BaseHandlerConfig):
    """Configuration for SysLogHandler."""
    
    class_: Literal["logging.handlers.SysLogHandler"] = Field(
        default="logging.handlers.SysLogHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    address: str | tuple[str, int] | None = Field(
        default=("localhost", 514),
        description="Syslog address"
    )
    facility: int | str | None = Field(
        default="user",
        description="Syslog facility"
    )
    socktype: int | None = Field(
        default=None,
        description="Socket type"
    )


class NTEventLogHandlerConfig(BaseHandlerConfig):
    """Configuration for NTEventLogHandler (Windows only)."""
    
    class_: Literal["logging.handlers.NTEventLogHandler"] = Field(
        default="logging.handlers.NTEventLogHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    appname: str = Field(
        description="Application name"
    )
    dllname: str | None = Field(
        default=None,
        description="DLL name"
    )
    logtype: str = Field(
        default="Application",
        description="Log type"
    )


class SMTPHandlerConfig(BaseHandlerConfig):
    """Configuration for SMTPHandler."""
    
    class_: Literal["logging.handlers.SMTPHandler"] = Field(
        default="logging.handlers.SMTPHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    mailhost: str | tuple[str, int] = Field(
        description="Mail server address"
    )
    fromaddr: str = Field(
        description="From email address"
    )
    toaddrs: str | list[str] = Field(
        description="To email addresses"
    )
    subject: str = Field(
        description="Email subject"
    )
    credentials: tuple[str, str] | None = Field(
        default=None,
        description="SMTP credentials (username, password)"
    )
    secure: tuple[str, str] | tuple[None, None] | None = Field(
        default=None,
        description="Use TLS"
    )
    timeout: float = Field(
        default=1.0,
        description="SMTP timeout"
    )


class MemoryHandlerConfig(BaseHandlerConfig):
    """Configuration for MemoryHandler."""
    
    class_: Literal["logging.handlers.MemoryHandler"] = Field(
        default="logging.handlers.MemoryHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    capacity: int = Field(
        description="Buffer capacity"
    )
    flushLevel: str | None = Field(
        default=None,
        description="Level at which to flush"
    )
    target: str | None = Field(
        default=None,
        description="Target handler name"
    )
    flushOnClose: bool = Field(
        default=True,
        description="Flush on handler close"
    )


class HTTPHandlerConfig(BaseHandlerConfig):
    """Configuration for HTTPHandler."""
    
    class_: Literal["logging.handlers.HTTPHandler"] = Field(
        default="logging.handlers.HTTPHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    host: str = Field(
        description="Web server host"
    )
    url: str = Field(
        description="URL path"
    )
    method: Literal["GET", "POST"] = Field(
        default="GET",
        description="HTTP method"
    )
    secure: bool = Field(
        default=False,
        description="Use HTTPS"
    )
    credentials: tuple[str, str] | None = Field(
        default=None,
        description="HTTP credentials"
    )
    context: dict[str, Any] | None = Field(
        default=None,
        description="SSL context"
    )


class QueueHandlerConfig(BaseHandlerConfig):
    """Configuration for QueueHandler."""
    
    class_: Literal["logging.handlers.QueueHandler"] = Field(
        default="logging.handlers.QueueHandler",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    queue: str = Field(
        description="Queue object reference"
    )


class QueueListenerConfig(BaseHandlerConfig):
    """Configuration for QueueListener."""
    
    class_: Literal["logging.handlers.QueueListener"] = Field(
        default="logging.handlers.QueueListener",
        validation_alias=AliasChoices("class_", "class"),
        serialization_alias="class"
    )
    queue: str = Field(
        description="Queue object reference"
    )
    handlers: list[str] = Field(
        description="Handler names"
    )
    respect_handler_level: bool = Field(
        default=False,
        description="Respect handler levels"
    )


# Union type for all handler configurations
HandlerConfig = StreamHandlerConfig | FileHandlerConfig | WatchedFileHandlerConfig | RotatingFileHandlerConfig | TimedRotatingFileHandlerConfig | SocketHandlerConfig | DatagramHandlerConfig | SysLogHandlerConfig | NTEventLogHandlerConfig | SMTPHandlerConfig | MemoryHandlerConfig | HTTPHandlerConfig | QueueHandlerConfig | QueueListenerConfig | BaseHandlerConfig  # For custom handlers


# Logger configuration
class LoggerConfig(BaseModel):
    """Configuration for a logger."""
    
    level: str | None = Field(
        default=None,
        description="Logging level"
    )
    propagate: bool | None = Field(
        default=None,
        description="Propagate to parent logger"
    )
    filters: list[str] | None = Field(
        default=None,
        description="List of filter IDs"
    )
    handlers: list[str] | None = Field(
        default=None,
        description="List of handler IDs"
    )


class RootLoggerConfig(BaseModel):
    """Configuration for the root logger."""
    
    level: str | None = Field(
        default="WARNING",
        description="Logging level"
    )
    filters: list[str] | None = Field(
        default=None,
        description="List of filter IDs"
    )
    handlers: list[str] | None = Field(
        default=None,
        description="List of handler IDs"
    )


# Custom settings sources
class TomlConfigSettingsSource(PydanticBaseSettingsSource):
    """Load settings from TOML file."""
    
    def __init__(
        self,
        settings_cls: type[BaseSettings],
        toml_file: str | None = None,
        toml_table: list[str] | None = None,
    ):
        super().__init__(settings_cls)
        self.toml_file = toml_file
        self.toml_table = toml_table
        self._data = self._load_file()
    
    def _load_file(self) -> dict[str, Any]:
        if not self.toml_file or not Path(self.toml_file).exists():
            return {}
        
        with open(self.toml_file, "rb") as f:
            data = tomllib.load(f)
        
        # Navigate to specified table if provided
        if self.toml_table:
            for key in self.toml_table:
                data = data.get(key, {})
                if not isinstance(data, dict):
                    return {}
        
        return data
    
    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        if field_name in self._data:
            return self._data[field_name], field_name, True
        return None, field_name, False
    
    def __call__(self) -> dict[str, Any]:
        return self._data


class JsonConfigSettingsSource(PydanticBaseSettingsSource):
    """Load settings from JSON file."""
    
    def __init__(
        self,
        settings_cls: type[BaseSettings],
        json_file: str | None = None,
    ):
        super().__init__(settings_cls)
        self.json_file = json_file
        self._data = self._load_file()
    
    def _load_file(self) -> dict[str, Any]:
        if not self.json_file or not Path(self.json_file).exists():
            return {}
        
        with open(self.json_file, "r") as f:
            return json.load(f)
    
    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        if field_name in self._data:
            return self._data[field_name], field_name, True
        return None, field_name, False
    
    def __call__(self) -> dict[str, Any]:
        return self._data


class IniConfigSettingsSource(PydanticBaseSettingsSource):
    """Load settings from INI file in logging.config.fileConfig format."""
    
    def __init__(
        self,
        settings_cls: type[BaseSettings],
        ini_file: str | None = None,
    ):
        super().__init__(settings_cls)
        self.ini_file = ini_file
        self._data = self._load_file()
    
    def _load_file(self) -> dict[str, Any]:
        if not self.ini_file or not Path(self.ini_file).exists():
            return {}
        
        config = ConfigParser(interpolation=None)
        config.read(self.ini_file)
        
        return self._convert_ini_to_dictconfig(config)
    
    def _convert_ini_to_dictconfig(self, config: ConfigParser) -> dict[str, Any]:
        """Convert INI format to dictConfig format."""
        result = {
            "version": 1,
            "formatters": {},
            "handlers": {},
            "loggers": {},
            "incremental": False,
            "disable_existing_loggers": True,
        }
        
        # Parse formatters
        if config.has_section("formatters"):
            formatter_keys = config.get("formatters", "keys", fallback="").split(",")
            for key in formatter_keys:
                key = key.strip()
                if key and config.has_section(f"formatter_{key}"):
                    result["formatters"][key] = self._parse_formatter_section(config, f"formatter_{key}")
        
        # Parse handlers  
        if config.has_section("handlers"):
            handler_keys = config.get("handlers", "keys", fallback="").split(",")
            for key in handler_keys:
                key = key.strip()
                if key and config.has_section(f"handler_{key}"):
                    result["handlers"][key] = self._parse_handler_section(config, f"handler_{key}")
        
        # Parse loggers
        if config.has_section("loggers"):
            logger_keys = config.get("loggers", "keys", fallback="").split(",")
            for key in logger_keys:
                key = key.strip()
                if key and config.has_section(f"logger_{key}"):
                    if key == "root":
                        result["root"] = self._parse_logger_section(config, f"logger_{key}", is_root=True)
                    else:
                        result["loggers"][key] = self._parse_logger_section(config, f"logger_{key}", is_root=False)
        
        # Parse global settings if they exist
        if config.has_option("DEFAULT", "disable_existing_loggers"):
            result["disable_existing_loggers"] = config.getboolean("DEFAULT", "disable_existing_loggers")
        
        return result
    
    def _parse_formatter_section(self, config: ConfigParser, section: str) -> dict[str, Any]:
        """Parse a formatter section."""
        formatter = {}
        
        if config.has_option(section, "format"):
            formatter["format"] = config.get(section, "format")
        if config.has_option(section, "datefmt"):
            datefmt = config.get(section, "datefmt")
            if datefmt:  # Only add if not empty
                formatter["datefmt"] = datefmt
        if config.has_option(section, "style"):
            formatter["style"] = config.get(section, "style")
        if config.has_option(section, "validate"):
            formatter["validate"] = config.getboolean(section, "validate")
        if config.has_option(section, "class"):
            formatter["class"] = config.get(section, "class")
        
        return formatter
    
    def _parse_handler_section(self, config: ConfigParser, section: str) -> dict[str, Any]:
        """Parse a handler section."""
        handler = {}
        
        if config.has_option(section, "class"):
            handler["class"] = config.get(section, "class")
        if config.has_option(section, "level"):
            handler["level"] = config.get(section, "level")
        if config.has_option(section, "formatter"):
            handler["formatter"] = config.get(section, "formatter")
        if config.has_option(section, "stream"):
            handler["stream"] = config.get(section, "stream")
        if config.has_option(section, "filename"):
            handler["filename"] = config.get(section, "filename")
        if config.has_option(section, "mode"):
            handler["mode"] = config.get(section, "mode")
        if config.has_option(section, "maxBytes"):
            handler["maxBytes"] = config.getint(section, "maxBytes")
        if config.has_option(section, "backupCount"):
            handler["backupCount"] = config.getint(section, "backupCount")
        if config.has_option(section, "when"):
            handler["when"] = config.get(section, "when")
        if config.has_option(section, "interval"):
            handler["interval"] = config.getint(section, "interval")
        if config.has_option(section, "utc"):
            handler["utc"] = config.getboolean(section, "utc")
        if config.has_option(section, "args"):
            # Handle args - this is complex as it can be a Python expression
            args_str = config.get(section, "args")
            # For basic cases, try to parse as a simple tuple
            if args_str == "()" or args_str == "()":
                handler["args"] = []
            elif args_str.startswith("(") and args_str.endswith(")"):
                # Store as string - the logging module will evaluate it
                handler["args"] = args_str
        
        # Add any other options as extra fields
        for option in config.options(section):
            if option not in ["class", "level", "formatter", "stream", "filename", "mode", 
                            "maxBytes", "backupCount", "when", "interval", "utc", "args"]:
                value = config.get(section, option)
                # Try to convert to appropriate type
                try:
                    # Try boolean
                    if value.lower() in ["true", "false"]:
                        handler[option] = config.getboolean(section, option)
                    # Try integer
                    elif value.isdigit():
                        handler[option] = config.getint(section, option)
                    else:
                        handler[option] = value
                except (ValueError, AttributeError):
                    handler[option] = value
        
        return handler
    
    def _parse_logger_section(self, config: ConfigParser, section: str, is_root: bool = False) -> dict[str, Any]:
        """Parse a logger section."""
        logger = {}
        
        if config.has_option(section, "level"):
            logger["level"] = config.get(section, "level")
        if config.has_option(section, "handlers"):
            handlers = config.get(section, "handlers")
            if handlers:
                logger["handlers"] = [h.strip() for h in handlers.split(",")]
        if not is_root and config.has_option(section, "propagate"):
            logger["propagate"] = config.getboolean(section, "propagate")
        if not is_root and config.has_option(section, "qualname"):
            # qualname is the logger name in INI format, but in dictConfig it's the key
            pass  # We handle this in the calling method
        
        return logger
    
    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        if field_name in self._data:
            return self._data[field_name], field_name, True
        return None, field_name, False
    
    def __call__(self) -> dict[str, Any]:
        return self._data



# Main LoggingSettings model
class LoggingSettings(BaseSettings):
    """Settings for Python logging configuration.
    
    Can be configured from multiple sources in priority order:
    1. Direct initialization parameters (highest priority)
    2. Environment variables (with configurable prefix, default: LOGGING_)
    3. logging.json - JSON configuration file
    4. logging.toml - TOML configuration file  
    5. logging.ini - INI configuration file (logging.config.fileConfig format)
    6. pyproject.toml [tool.logging] section (lowest priority)
    
    The model_dump() method returns a dictionary that can be passed
    directly to logging.config.dictConfig().
    """
    
    version: Literal[1] = Field(
        default=1,
        description="Configuration schema version"
    )
    formatters: dict[str, FormatterConfig] = Field(
        default_factory=dict,
        description="Formatter configurations"
    )
    filters: dict[str, FilterConfig] = Field(
        default_factory=dict,
        description="Filter configurations"
    )
    handlers: dict[str, Any] = Field(
        default_factory=dict,
        description="Handler configurations"
    )
    loggers: dict[str, LoggerConfig] = Field(
        default_factory=dict,
        description="Logger configurations"
    )
    root: RootLoggerConfig | None = Field(
        default=None,
        description="Root logger configuration"
    )
    incremental: bool = Field(
        default=False,
        description="Whether configuration is incremental"
    )
    disable_existing_loggers: bool = Field(
        default=True,
        description="Disable existing loggers"
    )
    
    model_config = SettingsConfigDict(
        env_prefix="LOGGING_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="allow",
    )
    
    def __new__(
        cls,
        *,
        env_prefix: str = "LOGGING_",
        json_file: str | None = None,
        toml_file: str | None = None,
        ini_file: str | None = None,
        **data: Any,
    ):
        """
        Create LoggingSettings with custom configuration sources.
        
        Args:
            env_prefix: Environment variable prefix (default: "LOGGING_")
            json_file: Path to JSON configuration file  
            toml_file: Path to TOML configuration file
            ini_file: Path to INI configuration file (logging.config.fileConfig format)
            **data: Additional settings to override
        """
        # If custom parameters are provided, create a dynamic class
        if (env_prefix != "LOGGING_" or json_file is not None or toml_file is not None or ini_file is not None):
            
            class CustomLoggingSettings(LoggingSettings):
                model_config = SettingsConfigDict(
                    env_prefix=env_prefix,
                    env_nested_delimiter="__",
                    case_sensitive=False,
                    extra="allow",
                )
                
                @classmethod
                def settings_customise_sources(
                    cls,
                    settings_cls: type[BaseSettings],
                    init_settings: PydanticBaseSettingsSource,
                    env_settings: PydanticBaseSettingsSource,
                    dotenv_settings: PydanticBaseSettingsSource,
                    file_secret_settings: PydanticBaseSettingsSource,
                ) -> tuple[PydanticBaseSettingsSource, ...]:
                    sources = []
                    
                    # Add sources in reverse priority order (first source has highest priority)
                    # Priority: init_settings > env > json > toml > ini > pyproject.toml
                    
                    # Add init_settings first (highest priority)
                    sources.append(init_settings)
                    
                    # Add environment variables
                    sources.extend([env_settings, dotenv_settings, file_secret_settings])
                    
                    # Add custom file sources
                    if json_file and Path(json_file).exists():
                        sources.append(JsonConfigSettingsSource(settings_cls, json_file=json_file))
                    elif Path("logging.json").exists():
                        sources.append(JsonConfigSettingsSource(settings_cls, json_file="logging.json"))
                    
                    if toml_file and Path(toml_file).exists():
                        sources.append(TomlConfigSettingsSource(settings_cls, toml_file=toml_file))
                    elif Path("logging.toml").exists():
                        sources.append(TomlConfigSettingsSource(settings_cls, toml_file="logging.toml"))
                    
                    if ini_file and Path(ini_file).exists():
                        sources.append(IniConfigSettingsSource(settings_cls, ini_file=ini_file))
                    elif Path("logging.ini").exists():
                        sources.append(IniConfigSettingsSource(settings_cls, ini_file="logging.ini"))
                    
                    # Add pyproject.toml source (lowest priority file)
                    if Path("pyproject.toml").exists():
                        sources.append(
                            TomlConfigSettingsSource(
                                settings_cls,
                                toml_file="pyproject.toml",
                                toml_table=["tool", "logging"],
                            )
                        )
                    
                    return tuple(sources)
            
            # Use the custom class instead
            return super(LoggingSettings, CustomLoggingSettings).__new__(CustomLoggingSettings)
        
        # Use the default class
        return super().__new__(cls)
    
    @field_validator("handlers", mode="before")
    @classmethod
    def validate_handlers(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate and convert handler configurations."""
        if not isinstance(v, dict):
            return v
        
        validated = {}
        for name, config in v.items():
            if isinstance(config, BaseModel):
                validated[name] = config
            elif isinstance(config, dict):
                # Try to determine handler type from class field
                handler_class = config.get("class", "")
                
                # Map class names to config models
                handler_map = {
                    "logging.StreamHandler": StreamHandlerConfig,
                    "logging.FileHandler": FileHandlerConfig,
                    "logging.handlers.WatchedFileHandler": WatchedFileHandlerConfig,
                    "logging.handlers.RotatingFileHandler": RotatingFileHandlerConfig,
                    "logging.handlers.TimedRotatingFileHandler": TimedRotatingFileHandlerConfig,
                    "logging.handlers.SocketHandler": SocketHandlerConfig,
                    "logging.handlers.DatagramHandler": DatagramHandlerConfig,
                    "logging.handlers.SysLogHandler": SysLogHandlerConfig,
                    "logging.handlers.NTEventLogHandler": NTEventLogHandlerConfig,
                    "logging.handlers.SMTPHandler": SMTPHandlerConfig,
                    "logging.handlers.MemoryHandler": MemoryHandlerConfig,
                    "logging.handlers.HTTPHandler": HTTPHandlerConfig,
                    "logging.handlers.QueueHandler": QueueHandlerConfig,
                    "logging.handlers.QueueListener": QueueListenerConfig,
                }
                
                # Use specific model if available, otherwise use base
                model_class = handler_map.get(handler_class, BaseHandlerConfig)
                try:
                    validated[name] = model_class(**config)
                except Exception:
                    # Fall back to raw dict for custom handlers
                    validated[name] = config
            else:
                validated[name] = config
        
        return validated
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize settings sources to load from multiple files."""
        sources = []
        
        # Add sources in reverse priority order (first source has highest priority)
        # Priority: init_settings > env > json > toml > ini > pyproject.toml
        
        # Add init_settings first (highest priority)
        sources.append(init_settings)
        
        # Add environment variables
        sources.extend([env_settings, dotenv_settings, file_secret_settings])
        
        if Path("logging.json").exists():
            sources.append(JsonConfigSettingsSource(settings_cls, json_file="logging.json"))
        
        if Path("logging.toml").exists():
            sources.append(TomlConfigSettingsSource(settings_cls, toml_file="logging.toml"))
        
        if Path("logging.ini").exists():
            sources.append(IniConfigSettingsSource(settings_cls, ini_file="logging.ini"))
        
        if Path("pyproject.toml").exists():
            sources.append(
                TomlConfigSettingsSource(
                    settings_cls,
                    toml_file="pyproject.toml",
                    toml_table=["tool", "logging"],
                )
            )
        
        return tuple(sources)
    
    def model_dump(self, **kwargs) -> dict[str, Any]:
        """
        Export configuration as a dictionary suitable for logging.dictConfig().
        
        This method ensures all handler configurations are properly serialized
        and removes any None values.
        """
        # Get base dump
        data = super().model_dump(exclude_none=True, by_alias=True, **kwargs)
        
        # Convert handler models to dicts
        if "handlers" in data:
            handlers = {}
            for name, handler in data["handlers"].items():
                if isinstance(handler, BaseModel):
                    handlers[name] = handler.model_dump(exclude_none=True, by_alias=True)
                else:
                    handlers[name] = handler
            data["handlers"] = handlers
        
        # Convert formatter models to dicts
        if "formatters" in data:
            formatters = {}
            for name, formatter in data["formatters"].items():
                if isinstance(formatter, BaseModel):
                    formatters[name] = formatter.model_dump(exclude_none=True, by_alias=True)
                else:
                    formatters[name] = formatter
            data["formatters"] = formatters
        
        # Convert filter models to dicts
        if "filters" in data:
            filters = {}
            for name, filter_config in data["filters"].items():
                if isinstance(filter_config, BaseModel):
                    filters[name] = filter_config.model_dump(exclude_none=True, by_alias=True)
                else:
                    filters[name] = filter_config
            data["filters"] = filters
        
        # Convert logger models to dicts
        if "loggers" in data:
            loggers = {}
            for name, logger in data["loggers"].items():
                if isinstance(logger, BaseModel):
                    loggers[name] = logger.model_dump(exclude_none=True)
                else:
                    loggers[name] = logger
            data["loggers"] = loggers
        
        # Convert root logger to dict
        if "root" in data and isinstance(data["root"], BaseModel):
            data["root"] = data["root"].model_dump(exclude_none=True)
        
        return data
