# API Reference

This document provides details on API usage within the AIR Plugin.

## 📌 `napari_experimental_provide_dock_widget()`
- **Returns**: A Napari dock widget for image filtering.

## 📌 `apply_grayscale(img)`
- **Description**: Converts an image to grayscale.
- **Parameters**: `img (ndarray)`

## 📌 `apply_edge_detection(img)`
- **Description**: Detects edges in an image.
- **Parameters**: `img (ndarray)`

## 📌 `apply_gaussian_blur(img, radius)`
- **Description**: Applies a Gaussian blur.
- **Parameters**:
  - `img (ndarray)`
  - `radius (float)`: Blur intensity

## 📌 AI Assistant (`GPT`)
- **Commands**:
  - `say(message)`: Sends a message to the AI.
  - `whisper(file_path)`: Transcribes audio input.

For detailed API usage, check the `src/` directory.