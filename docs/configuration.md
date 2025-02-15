# Configuration

This guide explains how to configure the **AIR Plugin** for proper functionality.

## Basic Configuration

### 1️⃣ Set Up Environment Variables

The AIR Plugin requires API keys for **AI features** such as voice recognition and image processing. To configure them:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in a text editor and fill in the required values.

### 2️⃣ Required API Keys

| Variable Name       | Description |
|---------------------|-------------|
| `OPENAI_API_KEY`   | API key for **ChatGPT** (used for AI interactions) |
| `HUGGINGFACE_API_KEY` | API key for **Hugging Face models** (if used) |
| `AI_PROMPT`        | System prompt for AI-generated responses |

Example `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
AI_PROMPT="You are an AI assistant helping with image processing."
```

### 3️⃣ Configure Napari

Ensure **Napari** is installed:
```bash
pip install napari
```
To verify installation, run:
```bash
python -c "import napari; print(napari.__version__)"
```

## Advanced Configuration

### 🔧 Modify Plugin Settings

To customize the plugin behavior, edit `mkdocs.yml` or `src/` files:
- **`mkdocs.yml`** → Adjust documentation settings.
- **`src/config.py`** (if applicable) → Change default parameters.

### 🔄 Updating Configuration
If changes are made to `.env`, restart the application:
```bash
source venv/bin/activate  # (On Windows use `venv\Scripts\activate`)
python main.py
```