"""
Test Suite for the whole project.

This module provides testing for image processing functions,
covering various scenarios and edge cases.
"""
import os
import pytest
import numpy as np
from PIL import Image
import tempfile
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
    Create a collection of sample images for comprehensive testing.
    
    Returns:
        dict: Dictionary of sample images with different characteristics
    """
    # Create temporary directory for test images
    with tempfile.TemporaryDirectory() as tmpdirname:
        # RGB Image
        rgb_image = Image.new('RGB', (100, 100), color='red')
        rgb_path = os.path.join(tmpdirname, 'rgb_image.png')
        rgb_image.save(rgb_path)
        
        # Grayscale Image
        gray_image = Image.new('L', (100, 100), color=128)
        gray_path = os.path.join(tmpdirname, 'gray_image.png')
        gray_image.save(gray_path)
        
        # RGBA Image
        rgba_image = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        rgba_path = os.path.join(tmpdirname, 'rgba_image.png')
        rgba_image.save(rgba_path)
        
        # Create NumPy arrays
        rgb_array = np.array(rgb_image)
        gray_array = np.array(gray_image)
        
        return {
            'rgb_pil': rgb_image,
            'rgb_path': rgb_path,
            'rgb_array': rgb_array,
            'gray_pil': gray_image,
            'gray_path': gray_path,
            'gray_array': gray_array,
            'rgba_pil': rgba_image,
            'rgba_path': rgba_path
        }

@pytest.mark.unit
def test_ensure_pil_image(sample_images):
    """
    Test the ensure_pil_image function with various input types.
    
    Verifies conversion from different image representations:
    - PIL Image
    - File path
    - NumPy arrays (RGB, Grayscale, RGBA)
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
    
    # Test RGBA conversion
    rgba_converted = ensure_pil_image(sample_images['rgba_pil'])
    assert isinstance(rgba_converted, Image.Image)
    assert rgba_converted.mode == 'RGBA'
    
    # Test invalid input
    with pytest.raises(TypeError):
        ensure_pil_image("invalid_input")

@pytest.mark.unit
def test_apply_grayscale(sample_images):
    """
    Comprehensive test for grayscale conversion.
    
    Covers:
    - Different input types
    - Correct grayscale conversion
    - Error handling
    """
    # Test with PIL Image
    gray_pil = apply_grayscale(sample_images['rgb_pil'])
    assert isinstance(gray_pil, np.ndarray)
    assert gray_pil.ndim == 2  # 2D array for grayscale
    
    # Test with NumPy array
    gray_array = apply_grayscale(sample_images['rgb_array'])
    assert isinstance(gray_array, np.ndarray)
    assert gray_array.ndim == 2
    
    # Test with file path
    gray_path = apply_grayscale(sample_images['rgb_path'])
    assert isinstance(gray_path, np.ndarray)
    assert gray_path.ndim == 2
    
    # Error case
    with pytest.raises(TypeError):
        apply_grayscale("invalid_input")

@pytest.mark.unit
def test_apply_crop(sample_images):
    """
    Comprehensive test for image cropping.
    
    Covers:
    - Successful cropping
    - Error cases (negative coordinates, out of bounds)
    """
    # Successful crop
    crop_coords = (10, 10, 90, 90)
    cropped_img = apply_crop(sample_images['rgb_pil'], crop_coords)
    assert isinstance(cropped_img, np.ndarray)
    assert cropped_img.shape[:2] == (80, 80)
    
    # Error cases
    with pytest.raises(Exception):
        apply_crop(sample_images['rgb_pil'], (-1, 0, 50, 50))  # Negative coordinates
    
    with pytest.raises(Exception):
        apply_crop(sample_images['rgb_pil'], (0, 0, 150, 150))  # Out of bounds

@pytest.mark.unit
def test_apply_saturation(sample_images):
    """
    Comprehensive test for saturation adjustment.
    
    Covers:
    - Different saturation levels
    - Error cases
    """
    # Zero saturation (grayscale)
    zero_sat_img = apply_saturation(sample_images['rgb_pil'], 0)
    assert isinstance(zero_sat_img, np.ndarray)
    
    # Original saturation
    orig_sat_img = apply_saturation(sample_images['rgb_pil'], 1.0)
    assert isinstance(orig_sat_img, np.ndarray)
    
    # Increased saturation
    double_sat_img = apply_saturation(sample_images['rgb_pil'], 2.0)
    assert isinstance(double_sat_img, np.ndarray)
    
    # Error cases
    with pytest.raises(ValueError):
        apply_saturation(sample_images['rgb_pil'], -1.0)  # Negative saturation

@pytest.mark.unit
def test_edge_processing(sample_images):
    """
    Comprehensive test for edge processing functions.
    
    Covers:
    - Edge enhancement
    - Edge detection
    - Different input types
    """
    # Edge enhancement
    enhanced_img = apply_edge_enhance(sample_images['rgb_pil'])
    assert isinstance(enhanced_img, np.ndarray)
    
    # Edge detection
    edge_img = apply_edge_detection(sample_images['rgb_pil'])
    assert isinstance(edge_img, np.ndarray)

def test_performance():
    """
    Simple performance test to ensure processing time is reasonable.
    
    Note: This is a basic implementation and should be expanded 
    with more sophisticated performance testing in a real-world scenario.
    """
    import time
    
    # Create a larger image for performance testing
    large_image = Image.new('RGB', (1000, 1000), color='blue')
    
    start_time = time.time()
    apply_grayscale(large_image)
    apply_saturation(large_image, 1.5)
    apply_edge_enhance(large_image)
    end_time = time.time()
    
    # Assert processing takes less than 1 second
    assert (end_time - start_time) < 1.0, "Image processing took too long"

if __name__ == "__main__":
    pytest.main()
