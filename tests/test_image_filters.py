"""
Test Suite for the whole project.

This module provides testing for image processing functions,
covering various scenarios and edge cases.
"""
import os
import pytest
import numpy as np
from PIL import Image

# Import the image processing functions
from src.napari_image_filters import (
    apply_grayscale,
    apply_crop,
    apply_saturation,
    apply_edge_enhance,
    apply_edge_detection,
    ensure_pil_image,
    apply_gaussian_blur,
    apply_contrast_enhancement,
    apply_texture_analysis,
    apply_adaptive_threshold,
    apply_sharpening,
    apply_ridge_detection,
    sanitize_dimensional_image
)


@pytest.mark.unit
def test_apply_gaussian_blur(sample_images):
    """
    Test Gaussian blur application with different parameters.
    """
    # Test with default radius
    blurred = apply_gaussian_blur(sample_images['rgb_pil'])
    assert isinstance(blurred, np.ndarray)
    assert blurred.shape == sample_images['rgb_array'].shape

    # Test with custom radius
    blurred_strong = apply_gaussian_blur(sample_images['rgb_pil'], radius=5.0)
    assert isinstance(blurred_strong, np.ndarray)

    # Test with grayscale image
    gray_blurred = apply_gaussian_blur(sample_images['gray_pil'])
    assert isinstance(gray_blurred, np.ndarray)
    assert gray_blurred.ndim == 2


@pytest.mark.unit
def test_apply_contrast_enhancement(sample_images):
    """
    Test contrast enhancement with different parameters.
    """
    # Test with default factor
    enhanced = apply_contrast_enhancement(sample_images['rgb_pil'])
    assert isinstance(enhanced, np.ndarray)
    assert enhanced.shape == sample_images['rgb_array'].shape

    # Test with custom factor
    enhanced_strong = apply_contrast_enhancement(
        sample_images['rgb_pil'], factor=2.5)
    assert isinstance(enhanced_strong, np.ndarray)

    # Test with grayscale image
    gray_enhanced = apply_contrast_enhancement(sample_images['gray_pil'])
    assert isinstance(gray_enhanced, np.ndarray)


@pytest.mark.unit
def test_apply_texture_analysis(sample_images):
    """
    Test texture analysis with different parameters.
    """
    # Test with default parameters
    texture = apply_texture_analysis(sample_images['rgb_pil'])
    assert isinstance(texture, np.ndarray)

    # Test with custom parameters
    texture_custom = apply_texture_analysis(
        sample_images['rgb_pil'],
        radius=2,
        n_points=12
    )
    assert isinstance(texture_custom, np.ndarray)

    # Test with grayscale image
    gray_texture = apply_texture_analysis(sample_images['gray_pil'])
    assert isinstance(gray_texture, np.ndarray)


@pytest.mark.unit
def test_apply_adaptive_threshold(sample_images):
    """
    Test adaptive thresholding with different parameters.
    """
    # Test with default parameters
    thresh = apply_adaptive_threshold(sample_images['rgb_pil'])
    assert isinstance(thresh, np.ndarray)

    # Test with custom parameters
    thresh_custom = apply_adaptive_threshold(
        sample_images['rgb_pil'],
        block_size=21,
        c=5
    )
    assert isinstance(thresh_custom, np.ndarray)

    # Test with grayscale image
    gray_thresh = apply_adaptive_threshold(sample_images['gray_pil'])
    assert isinstance(gray_thresh, np.ndarray)


@pytest.mark.unit
def test_apply_sharpening(sample_images):
    """
    Test image sharpening using a convolutional kernel.
    """
    # Convert sample images to NumPy arrays (if not already)
    rgb_array = np.array(sample_images['rgb_pil'])
    gray_array = np.array(sample_images['gray_pil'])

    # Test with RGB image
    sharp = apply_sharpening(rgb_array)
    assert isinstance(sharp, np.ndarray)
    assert sharp.shape == rgb_array.shape
    assert sharp.dtype == np.uint8

    # Ensure sharpening has an effect by checking pixel changes
    assert not np.array_equal(
        sharp, rgb_array), "Sharpening should modify the image"

    # Test with grayscale image
    gray_sharp = apply_sharpening(gray_array)
    assert isinstance(gray_sharp, np.ndarray)
    assert gray_sharp.shape == gray_array.shape
    assert gray_sharp.dtype == np.uint8
    assert not np.array_equal(
        gray_sharp, gray_array), "Sharpening should modify the grayscale image"


@pytest.mark.unit
def test_sanitize_dimensional_image(sample_images):
    """
    Test image dimension sanitization.
    """
    # Test with RGB image
    gray = sanitize_dimensional_image(sample_images['rgb_pil'])
    assert isinstance(gray, np.ndarray)
    assert gray.ndim == 2  # Should be 2D grayscale

    # Test with grayscale image
    gray_from_gray = sanitize_dimensional_image(sample_images['gray_pil'])
    assert isinstance(gray_from_gray, np.ndarray)
    assert gray_from_gray.ndim == 2


@pytest.mark.unit
def test_error_handling():
    """
    Test error handling in image processing functions.
    """
    # Test invalid radius for Gaussian blur
    with pytest.raises(ValueError):
        apply_gaussian_blur(np.zeros((10, 10)), radius=-1.0)

    # Test invalid saturation level
    with pytest.raises(ValueError):
        apply_saturation(np.zeros((10, 10)), saturation_level=-1.0)

    # Test invalid block size for adaptive threshold
    with pytest.raises(ValueError):
        apply_adaptive_threshold(np.zeros((10, 10)), block_size=-1)


@pytest.mark.unit
def test_input_type_handling(sample_images):
    """
    Test handling of different input types across functions.
    """
    # Test with NumPy array input
    functions_to_test = [
        apply_gaussian_blur,
        apply_contrast_enhancement,
        apply_texture_analysis,
        apply_adaptive_threshold,
        apply_sharpening,
        apply_ridge_detection
    ]

    for func in functions_to_test:
        # Test with RGB array
        result = func(sample_images['rgb_array'])
        assert isinstance(result, np.ndarray)

        # Test with grayscale array
        result = func(sample_images['gray_array'])
        assert isinstance(result, np.ndarray)

        # Test with file path
        result = func(sample_images['rgb_path'])
        assert isinstance(result, np.ndarray)


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


@pytest.mark.unit
def test_ridge_detection(sample_images):
    """
    Test ridge detection.
    """
    ridges_img = apply_ridge_detection(sample_images['gray_pil'])
    assert isinstance(ridges_img, np.ndarray)
    assert ridges_img.ndim == 2
