# Contributing

Table of contents:

- [Opening issues](#opening-issues)
  - [Bug reports](#bug-reports)
  - [Feature requests](#feature-requests)
- [Accepting new changes](#accepting-new-changes)
- [New releases](#new-releases)
- [Development environment](#development-environment)
  - [Prerequisites](#prerequisites)
  - [Install everything with uv](#install-everything-with-uv)
- [Testing](#testing)
  - [Running tests](#running-tests)

## Opening issues

### Bug reports

- Use the [issue template](https://github.com/vduseev/pydantic-settings-logging/issues/new/choose) when creating an issue.
- Provide a minimal reproducible example using strongly typed Pydantic models.
- Provide the full traceback.
- Provide the output of `uv pip freeze` and your Python version.

### Feature requests

- Describe the exact use case.
- Describe the input and output for the potential test case.
- Optionally, describe how you envision the feature to be implemented.
- Focus on strongly typed, validated logging configuration improvements.

## Accepting new changes

### Pull requests

1. Fork the repository.
1. Make your changes in your fork.
1. Run all tests and make sure they pass.
1. Push your commits to your fork.
1. Create a pull request from your fork to the original repository. Choose the
   `main` branch as the target branch or a specific branch you want to merge
   your changes into.
1. Get an approval from the maintainer.
1. Your changes will be merged into the original repository.
1. Once the maintainer collects all the changes, they will release a new version
   of the library.

### Code style

We use [ruff](https://github.com/astral-sh/ruff) for code style and linting.

### Testing requirements

- All new features must include strongly typed examples and tests
- Tests should demonstrate the type safety and validation benefits
- Handler configurations should use the appropriate typed config classes
- Examples in documentation should avoid raw dictionaries

## New releases

Here are the steps to publish a new version of the library:

1. Make sure everything you want to release is merged into the `main` branch.
1. Sync the dependencies with `uv sync`.
1. Run all tests and make sure they pass.
1. Bump the version using `uv version` and make sure the bump
   reflects the scope of changes:
   - `patch` for small changes, might be unnoticeable to users
   - `minor` for new features, might be noticeable to users
   - `major` for breaking changes or complete overhauls
1. Push new commit and tag created by `uv version` to GitHub.
1. Build the package with `uv build`.
1. Publish the package to PyPI using `uv publish`.

## Development environment

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

### Install everything with uv

```bash
uv sync
```

## Testing

### Running tests

Run tests with:

```bash
uv run pytest -x
```

For verbose output:

```bash
uv run pytest -x -v
```

To run a specific test:

```bash
uv run pytest tests/test_logger_settings.py::TestBasicConfiguration::test_minimal_configuration -v
```

### Test requirements

- Tests should use strongly typed Pydantic models wherever possible
- Avoid raw dictionary configurations in tests
- Test both the typed model creation AND the final dictConfig output
- Include tests for validation errors and type safety

### Example test pattern

```python
def test_strongly_typed_handler():
    """Test using strongly typed handler configuration."""
    from pydantic_settings_logging import LoggingSettings, RotatingFileHandlerConfig
    
    # Use typed configuration
    settings = LoggingSettings(
        handlers={
            "file": RotatingFileHandlerConfig(
                filename="test.log",
                maxBytes=1024,
                backupCount=3
            )
        }
    )
    
    # Verify the output is correct for dictConfig
    config = settings.model_dump()
    assert config["handlers"]["file"]["maxBytes"] == 1024
    
    # Verify it works with logging.dictConfig
    import logging.config
    logging.config.dictConfig(config)  # Should not raise
```
