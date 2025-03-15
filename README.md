# Venice Models for Continue

This utility helps you add Venice AI models to your Continue configuration with a simple command.

## What is Venice AI?

Venice AI provides high-quality AI models with a particular emphasis on code-related tasks. These models can be integrated with [Continue](https://continue.dev/), an open-source coding assistant.

## Installation

No installation is required beyond having Python 3 and the `requests` library. This script is designed to run with Nix, but can be used directly with Python.

## Usage

```bash
# If you have a api-key in your config.json, you can run:
./update.py

# Basic usage
./update.py --api-key your_venice_api_key

# Use environment variable for API key
export VENICE_API_KEY=your_venice_api_key
./update.py

# Dry run to see what changes would be made
./update.py --dry-run

# Specify a custom config path
./update.py --config-path /path/to/config.json
