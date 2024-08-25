# Trading Bot

This project is a customizable trading bot built for cryptocurrency trading on Binance. It leverages technical analysis indicators, scheduling, and logging to execute trading strategies automatically. The bot is built using Python and is designed to be modular, extendable, and easy to use.

## Features

- **Cryptocurrency Trading**: Uses Binance API for executing trades and fetching data.
- **Scheduler**: Automatically runs strategies at specified intervals using `schedule`.
- **Configuration**: Uses `yaml` for flexible configuration management.

## Table of Contents
- [Installation](#installation)


## Directory Structure

```bash
trading/
│
├── src/
│   ├── quants/
│   │   ├── algo/                  # Trading strategies and indicators
│   │   ├── auth/                  # Authentication and API handling
│   │   ├── config/                # Utilities like logging and config handling
│   │   ├── platform               # Main entry point for running the bot
│   │   ├── data_handler/          # Data handler for retrieving data from a exchange
│   │   └── task_scheduler/        # Scheduling tasks for a specific interval
├── tests/                         # Unit tests for the project
├── artifacts/config               # Example config file
├── pyproject.toml                 # Project and dependency configuration
├── README.md                      # Project documentation
└── Doxfile                        # Documentation for the project
```


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/vinittjain/quants.git
   cd quants
   ```
2. Set up a virtual environment and install dependencies
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -e .
    ```
3. Install development dependencies (optional):
    ```bash
    pip install .[dev]
    ```


## Development

1. Pre-commit Hooks - We use pre-commit hooks for code quality checks, including black, isort, and flake8. To enable hooks:
    ```bash
    pre-commit install
    ```
2. Running Tests - To run tests:
   ```bash
   pytest
   ```

3. Linting and Formatting - Ensure code is formatted and follows best practices before committing:
   ```bash
    black .
    isort .
    flake8
    mypy src/
    ```

4. Version Bumping - This will update the version in all relevant files (```__init__.py```,``` README.md```, and ```pyproject.toml```). To bump the project version:
   ```bash
   bumpversion minor
    ```


## License
This project is licensed under the MIT License. See the LICENSE file for details.

