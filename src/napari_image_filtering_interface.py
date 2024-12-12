"""
Napari Plugin Configuration and Widget

This module sets up the Napari plugin interface for image filtering.
"""
import napari
import numpy as np
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, 
    QLabel, QSlider, QHBoxLayout
)
from qtpy.QtCore import Qt
from .napari_image_filters import (
    apply_grayscale, apply_saturation, 
    apply_edge_enhance, apply_edge_detection,
    apply_gaussian_blur, apply_contrast_enhancement,
    apply_texture_analysis, apply_adaptive_threshold,
    apply_sharpening
)

from .chat_interface import (
    ChatWidget
)

class ImageFilterWidget(QWidget):
    """
    Custom Napari widget for image filtering operations.
    
    Provides interactive controls for:
    - Grayscale conversion
    - Saturation adjustment
    - Edge enhancement
    - Edge detection
    """
    
    def __init__(self, viewer: napari.Viewer):
        """
        Initialize the image filter widget.
        
        Args:
            viewer (napari.Viewer): The Napari viewer instance
        """
        super().__init__()
        self.viewer = viewer
        self.original_data = None
        # History stack for undo functionality
        self.history_stack = []
        self.max_history = 20  # Maximum number of undo steps

        # Create main layout
        layout = QVBoxLayout()

        # Add button layout at the top
        button_layout = QHBoxLayout()
        
        # Add Undo button
        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self._undo_last_change)
        self.undo_button.setEnabled(False)  # Disabled initially
        button_layout.addWidget(self.undo_button)
        
        # Add layout to main layout
        layout.addLayout(button_layout)
        
        # Saturation slider
        sat_layout = QHBoxLayout()
        self.sat_label = QLabel("Saturation: 1.0")
        self.sat_slider = QSlider(Qt.Horizontal)
        self.sat_slider.setMinimum(0)
        self.sat_slider.setMaximum(200)
        self.sat_slider.setValue(100)
        self.sat_slider.valueChanged.connect(self._update_saturation)
        sat_layout.addWidget(self.sat_label)
        sat_layout.addWidget(self.sat_slider)
        layout.addLayout(sat_layout)

        # Filter buttons
        filter_buttons = [
            ("Grayscale", self._apply_grayscale),
            ("Edge Enhance", self._apply_edge_enhance),
            ("Edge Detection", self._apply_edge_detection),
            ("Gaussian Blur", self._apply_gaussian_blur),
            ("Contrast Enhance", self._apply_contrast_enhancement),
            ("Texture Analysis", self._apply_texture_analysis),
            ("Adaptive Threshold", self._apply_adaptive_threshold),
            ("Sharpen", self._apply_sharpening)
        ]
        
        for name, method in filter_buttons:
            btn = QPushButton(name)
            btn.clicked.connect(method)
            layout.addWidget(btn)

        # Initialize the AI view
        self.chat_widget = ChatWidget(viewer, self)
        layout.addWidget(self.chat_widget)
        
        self.setLayout(layout)
    
    def _get_current_layer(self):
        """
        Retrieve the currently selected image layer.
        
        Returns:
            napari.layers.Image or None: Current image layer
        
        Raises:
            ValueError: If no image layer is selected
        """
        # Get the selected layers
        selected_layers = self.viewer.layers.selection
        
        # Check if any layers are selected
        if not selected_layers:
            # pdb.set_trace()
            raise ValueError("Please select an image layer")
        
        # Find the first image layer
        for layer in selected_layers:
            if isinstance(layer, napari.layers.Image):
                # Store original data for reset (The first time called)
                if self.original_data is None:
                    self.original_data = layer.data.copy()
                return layer
        
        # If no image layer is found
        raise ValueError("Please select an image layer")
    
    def _update_saturation(self, value):
        """
        Update saturation label based on slider position.
        
        Args:
            value (int): Slider value (0-200)
        """
        # Convert slider value to saturation multiplier
        sat_value = value / 100.0
        self.sat_label.setText(f"Saturation: {sat_value:.2f}")
        self._apply_saturation()


    def _push_to_history(self, layer):
        """
        Push current image state to history stack.
        
        Args:
            layer (napari.layers.Image): Current image layer
        """
        if len(self.history_stack) >= self.max_history:
            # Remove oldest history item if we exceed max history
            self.history_stack.pop(0)
        
        # Store a copy of the current state
        self.history_stack.append(layer.data.copy())
        
        # Enable undo button when we have history
        self.undo_button.setEnabled(True)

    def _undo_last_change(self):
        """
        Undo the last change by restoring the previous state.
        """
        try:
            layer = self._get_current_layer()
            
            if self.history_stack:
                # Restore the previous state
                layer.data = self.history_stack.pop()
                
                # Disable undo button if no more history
                if not self.history_stack:
                    self.undo_button.setEnabled(False)
            
        except Exception as e:
            print(f"Error undoing last change: {e}")
            import traceback
            traceback.print_exc()

    def _apply_filter(self, filter_func, reset=False):
        """
        Apply a filter to the current image layer.

        Args:
            filter_func (callable): Filter function to apply
            reset (bool): Whether to reset to original data before applying filter
        """
        try:
            # Get current layer
            layer = self._get_current_layer()
            
            # Store current state in history before applying filter
            self._push_to_history(layer)
            
            # Handle multi-dimensional image data
            original_data = layer.data
            
            if filter_func in [apply_edge_enhance, apply_edge_detection]:
                # Create a list to store filtered slices
                filtered_slices = []
                
                # Iterate through the first dimension
                for i in range(original_data.shape[0]):
                    # Apply filter to each 2D slice
                    slice_data = original_data[i]
                    filtered_slice = filter_func(slice_data)
                    
                    # Ensure filtered slice is a numpy array
                    if hasattr(filtered_slice, '__array__'):
                        filtered_slice = np.asarray(filtered_slice)
                    elif not isinstance(filtered_slice, np.ndarray):
                        filtered_slice = np.array(filtered_slice)
                    
                    filtered_slices.append(filtered_slice)
                
                # Reconstruct the multi-dimensional array
                filtered_array = np.stack(filtered_slices)
                
                # Store original data, so that we don't lose the build-up of filters
                self.original_data = layer.data.copy()
            else:
                if reset:
                    # Reset to the original data before applying the filter
                    original_data = self.original_data.copy()

                # Apply the filter
                filtered_array = filter_func(original_data)

                # Ensure filtered array is a numpy array
                if hasattr(filtered_array, '__array__'):
                    filtered_array = np.asarray(filtered_array)
                elif not isinstance(filtered_array, np.ndarray):
                    filtered_array = np.array(filtered_array)

            # Update layer
            layer.data = filtered_array
        
        except Exception as e:
            print(f"Error applying filter: {e}")
            import traceback
            traceback.print_exc()
    
    def _apply_saturation(self):
        """Apply saturation adjustment to current layer."""
        sat_value = self.sat_slider.value() / 100.0
        # Connect the saturation button to the filter method
        self._apply_filter(lambda img: apply_saturation(img, sat_value), True)

    def _apply_grayscale(self):
        """Apply grayscale filter to current layer."""
        self._apply_filter(apply_grayscale)

    def _apply_edge_enhance(self):
        """Apply edge enhancement to current layer."""
        self._apply_filter(apply_edge_enhance)
    
    def _apply_edge_detection(self):
        """Apply edge detection to current layer."""
        self._apply_filter(apply_edge_detection)

    def _apply_gaussian_blur(self):
        """Apply Gaussian blur to the current image"""
        self._apply_filter(apply_gaussian_blur)

    def _apply_contrast_enhancement(self):
        """Apply contrast enhancement to the current image"""
        self._apply_filter(apply_contrast_enhancement)

    def _apply_texture_analysis(self):
        """Apply texture analysis to the current image"""
        self._apply_filter(apply_texture_analysis)

    def _apply_adaptive_threshold(self):
        """Apply adaptive threshold to the current image"""
        self._apply_filter(apply_adaptive_threshold)

    def _apply_sharpening(self):
        """Apply sharpening to the current image"""
        self._apply_filter(apply_sharpening)

def napari_experimental_provide_dock_widget():
    """
    Napari plugin hook to provide the dock widget.
    
    Returns:
        callable: Function that creates the widget
    """
    def _widget_factory(viewer: napari.Viewer):
        return ImageFilterWidget(viewer)
    return _widget_factory
