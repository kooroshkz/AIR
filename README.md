# AIR
The Interactive Cell Segmentation Plugin for Napari allows biologists to control image analysis with voice commands. This plugin enables users to zoom, highlight areas, adjust contrast, and mark cells by simply speaking. The plugin makes cell segmentation and image enhancement faster and more intuitive, providing a simple way to interact with their data.

## Features

- Grayscale Conversion
- Saturation Adjustment
- Edge Enhancement
- Edge Detection
- Gaussian blur
- Contrast enhance 
- Texture analysis
- Adaptive treshold
- Image Sharpening

## Installation

### Prerequisites

- Python 3.8+
- Napari
- pip

## Usage

1. `python main.py`
2. Load an image
3. Open the "Image Filters" dock widget
4. Select an image layer
5. Apply filters using the provided controls

## Development

### Setup Development Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install development dependencies
pip install -e .[dev]

# Or if you want to install everything
pip install -r requirements.txt

# Setup .env 
Copy the .env.example into .env and then paste in the required fields into that .env file.
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src

# Run specific test markers
pytest -v -m unit
pytest -v -m integration
```

## What to remember when writing code here?
1) All requirements that are needed to run some .py program has to be put in requirements.txt
2) Write test cases for the code that you develop(I can then verify the future integrity of the code with automated testing)
## Where do I write my code?
Write your code as a component in src folder. If you want the final program to use your component then integrate your src folder component to main.py by importing it in main.py.
- For more information read the README in src
## What is main.py?
It runs our whole and complete application. So the end user should be able to run everything in the end with just:
```sh
python main.py
```
## How do I write good code?
Write in snake_case, always include docstrings, etc 
- Just make sure that when you push the file the pylint CICD process doesnt fail > It only fails if the code that was pushed is not written well
## What does the CICD do?
Currently it only formats the code, and checks for poorly written code. In the future this process will automatically run your tests.

