"""
Test Suite for Image Filter Interface

This module provides testing for the Napari plugin interface widget,
covering UI interactions and filter applications.
"""
import os
import pytest
import numpy as np
from unittest.mock import MagicMock, PropertyMock
from napari.layers import Image
import napari
from qtpy.QtWidgets import QApplication, QPushButton
from PIL import Image

# Import the widget class
from src.napari_image_filtering_interface import ImageFilterWidget


# Ensure QApplication exists
@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def viewer(qapp):
    """Create a mock napari viewer with proper layer structure."""
    viewer = MagicMock(spec=napari.Viewer)

    # Create layers mock
    layers = MagicMock()

    # Create an empty selection list that can be modified by tests
    selection = []
    type(layers).selection = PropertyMock(return_value=selection)

    # Attach layers to viewer
    type(viewer).layers = PropertyMock(return_value=layers)

    return viewer


@pytest.fixture
def image_layer():
    """Create a real napari image layer with test data."""
    base_path = os.path.join(os.path.dirname(__file__), "resources")
    image_path = os.path.join(base_path, "test_image.jpg")

    # Ensure the test image exists
    assert os.path.exists(image_path), f"Test image not found: {image_path}"

    # Load the test image and convert to numpy array
    base_image = Image.open(image_path)
    image_array = np.array(base_image)

    # Create napari layer from numpy array
    return napari.layers.Image(image_array)


@pytest.fixture
def widget(qapp, viewer):
    """Create the image filter widget with a mock viewer."""
    widget = ImageFilterWidget(viewer)
    return widget


def test_widget_initialization(widget):
    """Test widget initialization and UI element creation."""
    assert hasattr(widget, 'sat_slider')
    assert hasattr(widget, 'undo_button')
    assert hasattr(widget, 'viewer')
    assert widget.original_data is None
    assert len(widget.history_stack) == 0
    assert not widget.undo_button.isEnabled()
    assert widget.sat_slider.value() == 100


def test_filter_buttons_exist(widget):
    """Test that all filter buttons are present."""
    expected_buttons = {
        "view image filters",
        "send",
        "hold to record",
        "import workflow",
        "record",
        "stop",
        "set name",
        "save",
        "launch cellpipe"
    }

    buttons = {btn.text().lower() for btn in widget.findChildren(QPushButton)}
    assert expected_buttons.issubset(buttons)


def test_get_current_layer_no_selection(widget):
    """Test error handling when no layer is selected."""
    with pytest.raises(ValueError, match="Please select an image layer"):
        widget._get_current_layer()


def test_get_current_layer_success(widget, image_layer):
    """Test successful retrieval of current layer."""
    # Set up the selection property to return our image layer
    widget.viewer.layers.selection.append(image_layer)

    # Test the method
    result = widget._get_current_layer()
    assert isinstance(result, napari.layers.Image)
    assert np.array_equal(result.data, image_layer.data)


def test_history_stack_management(widget, image_layer):
    """Test history stack operations."""
    widget.viewer.layers.selection = [image_layer]

    # Push some states to history
    for _ in range(3):
        widget._push_to_history(image_layer)

    assert len(widget.history_stack) == 3
    assert widget.undo_button.isEnabled()


@pytest.mark.parametrize("filter_func", [
    "_apply_grayscale",
    "_apply_edge_enhance",
    "_apply_edge_detection",
    "_apply_gaussian_blur",
    "_apply_contrast_enhancement",
    "_apply_texture_analysis",
    "_apply_adaptive_threshold",
    "_apply_sharpening",
    "_apply_ridge_detection"
])
def test_filter_methods(widget, image_layer, filter_func):
    """Test that filter methods don't raise exceptions."""
    widget.viewer.layers.selection = [image_layer]
    method = getattr(widget, filter_func)
    method()  # Should not raise exception


def test_saturation_adjustment(widget, image_layer):
    """Test saturation slider functionality."""
    widget.viewer.layers.selection = [image_layer]
    widget.sat_slider.setValue(150)
    assert widget.sat_label.text() == "Saturation: 1.50"


def test_undo_functionality(widget, image_layer):
    """Test undo operation."""
    widget.viewer.layers.selection.append(image_layer)
    original_data = image_layer.data.copy()

    # Apply a change
    widget._push_to_history(image_layer)
    image_layer.data = np.zeros_like(original_data)

    # Test undo
    widget._undo_last_change()
    assert len(widget.history_stack) == 0


def test_napari_experimental_provide_dock_widget():
    """Test the napari plugin hook."""
    from src.napari_image_filtering_interface import napari_experimental_provide_dock_widget

    widget_factory = napari_experimental_provide_dock_widget()
    viewer = MagicMock(spec=napari.Viewer)
    widget = widget_factory(viewer)

    assert isinstance(widget, ImageFilterWidget)
