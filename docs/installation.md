# Installation Guide

## System Requirements

- Operating System: Windows 10+, macOS 10.15+, or Linux
- Python: Version 3.10 or higher

## Installation Methods

### Development Build From Source

```bash
git clone https://github.com/johk3/AIR.git
cd AIR
pip install -e .[dev]
```

Add all the necessary API keys and parameters to the .env file by copying the .env.example to .env and then changing .env.
```bash
cp .env.example .env
```

