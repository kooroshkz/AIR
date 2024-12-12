"""
Napari Plugin for Image Filtering and Processing

This module provides a set of image processing functions
that can be applied to images in the Napari viewer.

Key Features:
- Grayscale conversion
- Image cropping
- Saturation adjustment
- Edge enhancement
- Edge detection
"""
from typing import Union, Tuple
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

def ensure_pil_image(img: Union[Image.Image, np.ndarray, str]) -> Image.Image:
    """
    Convert input to PIL Image, handling different input types.
    
    Args:
        img (PIL.Image, numpy.ndarray, or str): Input image in various formats
    
    Returns:
        PIL.Image: Converted image
    
    Raises:
        TypeError: If input cannot be converted to PIL Image
    """
    # If already a PIL Image, return as-is
    if isinstance(img, Image.Image):
        return img
    
    # If string, open as image file
    if isinstance(img, str):
        return Image.open(img)
    
    # If NumPy array
    if isinstance(img, np.ndarray):
        # Handle different array shapes and data types
        # Ensure the array is uint8 to avoid potential conversion issues
        img_array = img.astype(np.uint8)
        
        # Handle different array dimensions
        if img_array.ndim == 2:
            # Grayscale image
            return Image.fromarray(img_array, mode='L')
        elif img_array.ndim == 3:
            # Check color channels
            if img_array.shape[2] == 3:
                # RGB image
                return Image.fromarray(img_array, mode='RGB')
            elif img_array.shape[2] == 4:
                # RGBA image
                return Image.fromarray(img_array, mode='RGBA')
            else:
                # Unusual channel count, try to convert to RGB
                if img_array.shape[2] == 1:
                    # Single channel, convert to grayscale
                    return Image.fromarray(img_array.squeeze(), mode='L')
                else:
                    # Try to take first 3 channels
                    return Image.fromarray(img_array[:,:,:3], mode='RGB')
        
        # If shape doesn't match expected formats
        raise TypeError(f"Unsupported NumPy array shape: {img.shape}")
    
    raise TypeError("Input must be a PIL Image, NumPy array, or valid image path")

def apply_grayscale(img: Union[Image.Image, np.ndarray, str]) -> np.ndarray:
    """
    Convert an image to grayscale.
    
    Args:
        img (PIL.Image, numpy.ndarray, or str): Input image in various formats
    
    Returns:
        numpy.ndarray: Grayscale version of the input image
    """
    # Ensure input is a PIL Image
    pil_img = ensure_pil_image(img)
    
    # Convert to grayscale
    grayscale_pil = pil_img.convert("L")
    
    # Convert back to numpy array
    grayscale_array = np.array(grayscale_pil)

    # If the input was a 3D array, maintain the 3D shape for consistency
    if isinstance(img, np.ndarray) and img.ndim == 3:
        return grayscale_array[:, :, np.newaxis]
    
    # Otherwise return the 2D array
    return grayscale_array

def apply_crop(img: Union[Image.Image, np.ndarray, str], 
               corners: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Crop an image based on provided corner coordinates.
    
    Args:
        img (PIL.Image, numpy.ndarray, or str): Input image
        corners (tuple): (left, upper, right, lower) coordinates
    
    Returns:
        numpy.ndarray: Cropped image
    
    Raises:
        Exception: If coordinates are invalid
    """
    # Ensure input is a PIL Image
    pil_img = ensure_pil_image(img)
    
    # Check for negative values
    if any(val < 0 for val in corners):
        raise Exception("Coordinates cannot be negative")
    
    # Check coordinate bounds
    x_range, y_range = pil_img.size
    if (corners[0] > x_range or corners[2] > x_range or
        corners[1] > y_range or corners[3] > y_range):
        raise Exception("Coordinates exceed image dimensions")
    
    # Crop and convert to numpy array
    return np.array(pil_img.crop(corners))

def apply_saturation(img: Union[Image.Image, np.ndarray, str], 
                     saturation_level: float) -> np.ndarray:
    """
    Adjust image saturation.
    
    Args:
        img (PIL.Image, numpy.ndarray, or str): Input image
        saturation_level (float): Saturation multiplier
            0.0 = grayscale
            1.0 = original saturation
            > 1.0 = increased saturation
    
    Returns:
        numpy.ndarray: Saturated image
    
    Raises:
        ValueError: If saturation level is invalid
    """
    # Ensure input is a PIL Image
    pil_img = ensure_pil_image(img)
    
    # Validate saturation level
    if saturation_level < 0:
        raise ValueError("Saturation level cannot be negative")
    
    # Apply saturation
    enhancer = ImageEnhance.Color(pil_img)
    saturated_pil = enhancer.enhance(saturation_level)

    # Convert back to numpy array
    return np.array(saturated_pil)

def apply_edge_enhance(img: Union[Image.Image, np.ndarray, str]) -> np.ndarray:
    """
    Enhance edges in the image.
    
    Args:
        img (PIL.Image, numpy.ndarray, or str): Input image
    
    Returns:
        numpy.ndarray: Edge-enhanced image
    """
    # Ensure input is a PIL Image
    pil_img = ensure_pil_image(img)
    
    # Apply edge enhancement
    enhanced_pil = pil_img.filter(ImageFilter.EDGE_ENHANCE)
    
    # Convert back to numpy array
    return np.array(enhanced_pil)

def apply_edge_detection(img: Union[Image.Image, np.ndarray, str]) -> np.ndarray:
    """
    Detect edges in the image.
    
    Args:
        img (PIL.Image, numpy.ndarray, or str): Input image
    
    Returns:
        numpy.ndarray: Edge-detected image
    """
    # Ensure input is a PIL Image
    pil_img = ensure_pil_image(img)
    
    # Apply edge detection
    edge_pil = pil_img.filter(ImageFilter.FIND_EDGES)
    
    # Convert back to numpy array
    return np.array(edge_pil)
