# Installation Guide

## System Requirements

- Operating System: Windows 10+, macOS 10.15+, or Linux
- Python: Version 3.10 or higher

## Installation Methods

### Build From Source

```bash
git clone https://github.com/johk3/AIR.git
cd AIR

# Optional(if you already use conda or something else)
# Setup the virtual environment
python -m venv .venv
# Activate the virtual environment
source .venv/bin/activate


# Install all required packages for development
pip install -e .[dev]
```

Add all the necessary API keys and parameters to the .env file by copying the .env.example to .env and then changing .env.
```bash
cp .env.example .env
```

Afterwards you can run the program with 
```bash
python main.py
```

## Contributing
For further information about contributing visit: [How to Contribute](contributing.md)
