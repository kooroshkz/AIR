"""
Test Suite for the whole project.

This module provides testing for image processing functions,
covering various scenarios and edge cases.
"""
import os
import pytest
import numpy as np
from PIL import Image
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import the image processing functions
from napari_image_filters import (
    apply_grayscale,
    apply_crop,
    apply_saturation,
    apply_edge_enhance,
    apply_edge_detection,
    ensure_pil_image
)

@pytest.fixture(scope="module")
def sample_images():
    """
    Load the test image and prepare various representations for testing.

    Returns:
        dict: Dictionary of sample images with different characteristics.
    """
    base_path = os.path.join(os.path.dirname(__file__), "resources")
    image_path = os.path.join(base_path, "test_image.jpg")

    # Ensure the test image exists
    assert os.path.exists(image_path), f"Test image not found: {image_path}"

    # Load the test image
    base_image = Image.open(image_path)

    # Prepare different formats
    rgb_array = np.array(base_image)
    gray_image = base_image.convert("L")
    gray_array = np.array(gray_image)

    return {
        'rgb_pil': base_image,
        'rgb_path': image_path,
        'rgb_array': rgb_array,
        'gray_pil': gray_image,
        'gray_array': gray_array
    }

@pytest.mark.unit
def test_ensure_pil_image(sample_images):
    """
    Test the ensure_pil_image function with various input types.
    """
    # Test PIL Image conversion
    assert isinstance(ensure_pil_image(sample_images['rgb_pil']), Image.Image)
    
    # Test file path conversion
    assert isinstance(ensure_pil_image(sample_images['rgb_path']), Image.Image)
    
    # Test RGB NumPy array conversion
    rgb_converted = ensure_pil_image(sample_images['rgb_array'])
    assert isinstance(rgb_converted, Image.Image)
    assert rgb_converted.mode == 'RGB'
    
    # Test Grayscale NumPy array conversion
    gray_converted = ensure_pil_image(sample_images['gray_array'])
    assert isinstance(gray_converted, Image.Image)
    assert gray_converted.mode == 'L'

@pytest.mark.unit
def test_apply_grayscale(sample_images):
    """
    Test grayscale conversion.
    """
    gray_array = apply_grayscale(sample_images['rgb_pil'])
    assert isinstance(gray_array, np.ndarray)
    assert gray_array.ndim == 2

@pytest.mark.unit
def test_apply_crop(sample_images):
    """
    Test image cropping.
    """
    crop_coords = (10, 10, 90, 90)
    cropped_img = apply_crop(sample_images['rgb_pil'], crop_coords)
    assert isinstance(cropped_img, np.ndarray)
    assert cropped_img.shape[:2] == (80, 80)

@pytest.mark.unit
def test_apply_saturation(sample_images):
    """
    Test saturation adjustment.
    """
    saturated_img = apply_saturation(sample_images['rgb_pil'], 1.5)
    assert isinstance(saturated_img, np.ndarray)

@pytest.mark.unit
def test_edge_processing(sample_images):
    """
    Test edge processing functions.
    """
    enhanced_img = apply_edge_enhance(sample_images['rgb_pil'])
    assert isinstance(enhanced_img, np.ndarray)

    edge_img = apply_edge_detection(sample_images['rgb_pil'])
    assert isinstance(edge_img, np.ndarray)
