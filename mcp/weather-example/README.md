# weather-example

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that exposes US weather data from the [National Weather Service API](https://www.weather.gov/documentation/services-web-api) as tools that AI assistants can call.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [MCP Tools](#mcp-tools)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

`weather-example` is a minimal, self-contained MCP server written in Python. It wraps two endpoints of the free, no-auth-required [api.weather.gov](https://api.weather.gov) API and exposes them as MCP tools that any MCP-compatible client (Claude Desktop, Cursor, etc.) can call.

The server communicates over **stdio** transport, making it easy to integrate with any host that supports the MCP specification.

---

## Features

- **Active weather alerts** – retrieve all current alerts for any US state.
- **Point forecast** – retrieve a multi-period forecast for any US latitude/longitude.
- Zero external API keys required — uses the public NWS API.
- Async from top to bottom (`httpx`, `FastMCP`).
- Linted with [Ruff](https://docs.astral.sh/ruff/), tested with [pytest](https://pytest.org), managed with [uv](https://docs.astral.sh/uv/).
- Build automation via [Invoke](https://www.pyinvoke.org/).

---

## Requirements

| Tool | Version |
|------|---------|
| Python | >= 3.10 |
| [uv](https://docs.astral.sh/uv/) | latest |

> **Note:** `uv` manages the virtual environment and all dependencies automatically. You do not need to create a virtualenv manually.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/ocrosby/python-lab.git
cd python-lab/mcp/weather-example

# Install all dependencies (runtime + dev)
uv sync --all-extras --all-groups
```

Or via the provided Invoke task:

```bash
uv run invoke install
```

---

## Usage

### Run the server directly

```bash
uv run weather
```

The server starts and listens on **stdio** for MCP messages.

### Via Invoke

```bash
uv run invoke run
```

### Connecting to Claude Desktop

Add the following to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/python-lab/mcp/weather-example",
        "run",
        "weather"
      ]
    }
  }
}
```

After saving, restart Claude Desktop. The `get_alerts` and `get_forecast` tools will be available automatically.

---

## MCP Tools

### `get_alerts`

Retrieve all active weather alerts for a US state.

| Parameter | Type | Description |
|-----------|------|-------------|
| `state` | `str` | Two-letter US state code (e.g. `CA`, `NY`, `TX`) |

**Example response:**

```
Event: Tornado Warning
Area: Central TX
Severity: Extreme
Description: A tornado was spotted near ...
Instructions: Take shelter immediately.
```

---

### `get_forecast`

Retrieve the next five forecast periods for a geographic location.

| Parameter | Type | Description |
|-----------|------|-------------|
| `latitude` | `float` | Latitude of the location |
| `longitude` | `float` | Longitude of the location |

**Example response:**

```
Tonight:
  Temperature: 55°F
  Wind: 10 mph NW
  Forecast: Clear skies with a low near 55.
---
Wednesday:
  Temperature: 72°F
  Wind: 5 mph S
  Forecast: Partly sunny, with a high near 72.
```

> Coverage is limited to the continental United States, Alaska, Hawaii, and US territories served by the NWS API.

---

## Project Structure

```
weather-example/
├── src/
│   └── weather/
│       ├── __init__.py
│       └── server.py       # FastMCP server, tool definitions
├── tests/
│   ├── __init__.py
│   └── test_server.py      # pytest test suite
├── tasks.py                # Invoke build tasks
├── pyproject.toml          # Project metadata, dependencies, tool config
└── uv.lock                 # Locked dependency graph
```

---

## Development

All common development tasks are available as Invoke tasks:

```bash
# Install dependencies
uv run invoke install

# Auto-format code
uv run invoke fmt

# Lint (check only)
uv run invoke lint

# Lint and auto-fix
uv run invoke lint-fix

# Run tests
uv run invoke test

# Run tests with verbose output
uv run invoke test --verbose

# Run tests with coverage report
uv run invoke test --cov

# Full pipeline: format → lint → test
uv run invoke build

# Remove build artefacts and caches
uv run invoke clean
```

### Code style

This project uses [Ruff](https://docs.astral.sh/ruff/) for both formatting and linting. The configuration lives in `pyproject.toml` under `[tool.ruff]`. Key settings:

- Line length: **88** characters
- Target Python: **3.10+**
- Enabled rule sets: `E`, `F`, `I`, `UP`, `B`, `S`, `ANN`

---

## Testing

Tests live in `tests/` and are run with `pytest`. The suite uses `pytest-asyncio` (auto mode) and `pytest-mock` for mocking the async HTTP client.

```bash
# Run the full test suite
uv run pytest

# With verbose output
uv run pytest -v

# With coverage (requires pytest-cov)
uv run pytest --cov=src/weather --cov-report=term-missing
```

### What is tested

- `make_nws_request` – successful responses and HTTP errors.
- `format_alert` – full properties and missing/defaulted properties.
- `get_alerts` – formatted output, no alerts, API failure, missing keys, multiple alerts.
- `get_forecast` – success path, points failure, forecast failure, period limit (max 5).

---

## Configuration

The server has no required configuration. The following constants in `src/weather/server.py` can be adjusted if needed:

| Constant | Default | Description |
|----------|---------|-------------|
| `NWS_API_BASE` | `https://api.weather.gov` | Base URL for the NWS API |
| `USER_AGENT` | `weather-app/1.0` | `User-Agent` header sent with requests |

NWS requests use a 30-second timeout and are fully unauthenticated.

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/my-feature`.
3. Make your changes and add tests.
4. Run the full build pipeline to verify everything passes:
   ```bash
   uv run invoke build
   ```
5. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/).
6. Open a pull request against `main`.

Please keep pull requests focused on a single change to make review straightforward.

### Reporting bugs

Open an issue on GitHub and include:
- Python version (`python --version`)
- `uv` version (`uv --version`)
- Steps to reproduce
- Expected vs. actual behavior

---

## License

This project is part of [python-lab](https://github.com/ocrosby/python-lab) and is released under the [MIT License](../../LICENSE).
