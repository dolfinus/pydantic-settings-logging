"""Test direct instantiation of models with class_ field."""

import pytest
from pydantic import ValidationError

from pydantic_settings_logging import (
    BaseHandlerConfig,
    StreamHandlerConfig,
    FileHandlerConfig,
    FormatterConfig,
    FilterConfig,
)


def test_base_handler_config_direct_instantiation():
    """Test that BaseHandlerConfig can be instantiated directly with class_ parameter."""
    # Should work with field name (class_)
    handler = BaseHandlerConfig(class_="logging.StreamHandler")
    assert handler.class_ == "logging.StreamHandler"
    
    # Should serialize with alias (class) when using by_alias=True
    data = handler.model_dump(by_alias=True)
    assert data["class"] == "logging.StreamHandler"
    assert "class_" not in data


def test_stream_handler_config_direct_instantiation():
    """Test that StreamHandlerConfig can be instantiated directly with class_ parameter."""
    # Should work with field name (class_)
    handler = StreamHandlerConfig(class_="logging.StreamHandler")
    assert handler.class_ == "logging.StreamHandler"
    
    # Should serialize with alias (class) when using by_alias=True
    data = handler.model_dump(by_alias=True)
    assert data["class"] == "logging.StreamHandler"
    assert "class_" not in data


def test_file_handler_config_direct_instantiation():
    """Test that FileHandlerConfig can be instantiated directly with class_ parameter."""
    # Should work with field name (class_)
    handler = FileHandlerConfig(class_="logging.FileHandler", filename="test.log")
    assert handler.class_ == "logging.FileHandler"
    assert handler.filename == "test.log"
    
    # Should serialize with alias (class) when using by_alias=True
    data = handler.model_dump(by_alias=True)
    assert data["class"] == "logging.FileHandler"
    assert data["filename"] == "test.log"
    assert "class_" not in data


def test_formatter_config_direct_instantiation():
    """Test that FormatterConfig can be instantiated directly with class_ parameter."""
    # Should work with field name (class_)
    formatter = FormatterConfig(class_="logging.Formatter")
    assert formatter.class_ == "logging.Formatter"
    
    # Should serialize with alias (class) when using by_alias=True
    data = formatter.model_dump(by_alias=True)
    assert data["class"] == "logging.Formatter"
    assert "class_" not in data


def test_filter_config_direct_instantiation():
    """Test that FilterConfig can be instantiated directly with class_ parameter."""
    # Should work with field name (class_)
    filter_config = FilterConfig(class_="logging.Filter")
    assert filter_config.class_ == "logging.Filter"
    
    # Should serialize with alias (class) when using by_alias=True
    data = filter_config.model_dump(by_alias=True)
    assert data["class"] == "logging.Filter"
    assert "class_" not in data


def test_config_from_dict_with_alias():
    """Test that models can still be created from dict using alias."""
    # Should work with alias (class) from dict
    data = {"class": "logging.StreamHandler", "level": "INFO"}
    handler = BaseHandlerConfig(**data)
    assert handler.class_ == "logging.StreamHandler"
    assert handler.level == "INFO"


def test_config_validation_from_dict():
    """Test that validation works with dict input using alias."""
    # Should work with alias (class) from dict
    data = {"class": "logging.FileHandler", "filename": "test.log"}
    handler = FileHandlerConfig.model_validate(data)
    assert handler.class_ == "logging.FileHandler"
    assert handler.filename == "test.log"


def test_both_field_name_and_alias_work():
    """Test that both field name and alias work for instantiation."""
    # Create with field name
    handler1 = BaseHandlerConfig(class_="logging.StreamHandler")
    
    # Create with dict using alias
    handler2 = BaseHandlerConfig.model_validate({"class": "logging.StreamHandler"})
    
    # Both should have same values
    assert handler1.class_ == handler2.class_ == "logging.StreamHandler"
    
    # Both should serialize the same way when using by_alias=True
    assert handler1.model_dump(by_alias=True) == handler2.model_dump(by_alias=True)


def test_cannot_use_class_as_keyword():
    """Test that using 'class' as keyword argument fails (Python limitation)."""
    # This should fail because 'class' is a reserved keyword in Python
    with pytest.raises(SyntaxError):
        # This line should cause a syntax error during parsing
        exec("BaseHandlerConfig(class='logging.StreamHandler')")


def test_mixed_instantiation_styles():
    """Test mixing field names and aliases in different contexts."""
    # Direct instantiation with field name
    handler = FileHandlerConfig(
        class_="logging.FileHandler",
        filename="test.log",
        level="INFO"
    )
    
    # Serialize to dict (should use aliases when by_alias=True)
    data = handler.model_dump(by_alias=True, exclude_none=True)
    expected = {
        "class": "logging.FileHandler",
        "filename": "test.log",
        "level": "INFO",
        "mode": "a",
        "delay": False
    }
    assert data == expected
    
    # Recreate from dict (should use aliases)
    handler2 = FileHandlerConfig.model_validate(data)
    assert handler2.class_ == "logging.FileHandler"
    assert handler2.filename == "test.log"
    assert handler2.level == "INFO"