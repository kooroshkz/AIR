import subprocess
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
)
from qtpy.QtCore import Qt
import numpy as np

try:
    from cellpose import models
    CELLPOSE_AVAILABLE = True
except ImportError:
    CELLPOSE_AVAILABLE = False


class CellposeNapariWidget(QWidget):
    """Embedded Cellpose widget for Napari"""

    def __init__(self, viewer, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.cellpose_gui = None

        layout = QVBoxLayout()

        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_selector = QComboBox()
        self.model_selector.addItems(["cyto", "nuclei", "tissuenet"])
        model_layout.addWidget(self.model_selector)
        layout.addLayout(model_layout)

        # Parameters
        params_layout = QVBoxLayout()

        # Diameter
        diameter_layout = QHBoxLayout()
        diameter_layout.addWidget(QLabel("Cell Diameter:"))
        self.diameter_spin = QSpinBox()
        self.diameter_spin.setRange(0, 500)
        self.diameter_spin.setValue(30)
        self.diameter_spin.setSingleStep(5)
        diameter_layout.addWidget(self.diameter_spin)
        params_layout.addLayout(diameter_layout)

        # Flow threshold
        flow_layout = QHBoxLayout()
        flow_layout.addWidget(QLabel("Flow Threshold:"))
        self.flow_spin = QDoubleSpinBox()
        self.flow_spin.setRange(0, 1)
        self.flow_spin.setValue(0.4)
        self.flow_spin.setSingleStep(0.05)
        flow_layout.addWidget(self.flow_spin)
        params_layout.addLayout(flow_layout)

        # Cellprob threshold
        prob_layout = QHBoxLayout()
        prob_layout.addWidget(QLabel("Cell Probability Threshold:"))
        self.prob_spin = QDoubleSpinBox()
        self.prob_spin.setRange(-6, 6)
        self.prob_spin.setValue(0.0)
        self.prob_spin.setSingleStep(0.5)
        prob_layout.addWidget(self.prob_spin)
        params_layout.addLayout(prob_layout)

        # Additional options
        self.use_gpu = QCheckBox("Use GPU (if available)")
        self.use_gpu.setChecked(True)
        params_layout.addWidget(self.use_gpu)

        layout.addLayout(params_layout)

        # Control buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Run Segmentation")
        self.run_button.clicked.connect(self.run_segmentation)
        button_layout.addWidget(self.run_button)

        self.apply_button = QPushButton("Apply to Napari")
        self.apply_button.clicked.connect(self.apply_to_napari)
        self.apply_button.setEnabled(False)
        button_layout.addWidget(self.apply_button)

        layout.addLayout(button_layout)

        # Status
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.masks = None
        self.flows = None

        # Check if cellpose is available
        if not CELLPOSE_AVAILABLE:
            self.status_label.setText("Error: Cellpose not installed")
            self.run_button.setEnabled(False)
            self.apply_button.setEnabled(False)

    def get_current_image(self):
        """Get the currently selected image from Napari"""
        selected_layers = self.viewer.layers.selection
        for layer in selected_layers:
            if hasattr(layer, 'data') and isinstance(layer.data, np.ndarray):
                return layer.data, layer.name
        self.status_label.setText("Error: No image layer selected")
        return None, None

    def run_segmentation(self):
        """Run Cellpose segmentation on the current image"""
        image_data, layer_name = self.get_current_image()
        if image_data is None:
            return

        try:
            self.status_label.setText("Running segmentation...")
            model_type = self.model_selector.currentText()
            diameter = self.diameter_spin.value() if self.diameter_spin.value() > 0 else None

            # Initialize model
            model = models.Cellpose(
                gpu=self.use_gpu.isChecked(),
                model_type=model_type
            )

            # Prepare channels based on image dimensionality
            if image_data.ndim == 2:  # Grayscale
                channels = [0, 0]
            elif image_data.ndim == 3 and image_data.shape[2] >= 3:  # RGB
                channels = [0, 0]  # Default to first channel
            else:
                channels = [0, 0]

            # Run the model - handle variable number of return values
            model_output = model.eval(
                image_data,
                diameter=diameter,
                channels=channels,
                flow_threshold=self.flow_spin.value(),
                cellprob_threshold=self.prob_spin.value()
            )

            # Unpack only what we need, allowing for extra return values in
            # newer cellpose versions
            if isinstance(model_output, tuple):
                masks = model_output[0]
                flows = model_output[1] if len(model_output) > 1 else None
            else:
                masks = model_output
                flows = None

            self.masks = masks
            self.flows = flows
            self.apply_button.setEnabled(True)
            self.status_label.setText(
                f"Segmentation complete: Found {len(np.unique(masks)) - 1} cells")

            # Show preview in Napari
            self.viewer.add_labels(
                masks, name=f"{layer_name}_cellpose_preview", opacity=0.5)

        except Exception as e:
            self.status_label.setText(f"Error during segmentation: {str(e)}")

    def apply_to_napari(self):
        """Apply the segmentation results to Napari"""
        if self.masks is not None:
            image_data, layer_name = self.get_current_image()
            if image_data is None:
                return

            # Remove preview if it exists
            preview_name = f"{layer_name}_cellpose_preview"
            for layer in list(self.viewer.layers):
                if layer.name == preview_name:
                    self.viewer.layers.remove(layer)

            # Add the final masks layer
            self.viewer.add_labels(
                self.masks, name=f"{layer_name}_cellpose_masks")

            # adds flow layers for visualization(No idea if this is actually
            # useful or not)
            if self.flows is not None and len(self.flows) > 0:
                self.viewer.add_image(
                    self.flows[0],
                    name=f"{layer_name}_flows_y",
                    colormap='blues')
                self.viewer.add_image(
                    self.flows[1],
                    name=f"{layer_name}_flows_x",
                    colormap='reds')
                pass

            self.status_label.setText("Results applied to Napari")


class CellposeLaunchPoint(QWidget):
    """
    Widget for launching Cellpose integrated with Napari
    """

    def __init__(self, viewer, filter_widget):
        super().__init__()
        self.viewer = viewer
        self.filter_widget = filter_widget
        self.launch_btn = QPushButton("Launch CellPipe")  # the final stage
        self.launch_btn.setToolTip(
            "Launch Cellpose integrated with Napari\nUsing this, you can finalize your pipeline with a variety of segmentation models\nChanges will be applied directly to the Napari viewer"
        )
        self.cellpose_widget = None
        self.setup_ui()

    def setup_ui(self):
        self.launch_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0366d6;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0255b3;
            }
            """
        )
        self.launch_btn.clicked.connect(self._launch_cellpipe)

        layout = QHBoxLayout()
        layout.addWidget(self.launch_btn)

        self.setLayout(layout)

    def _launch_cellpipe(self) -> None:
        """Launch Cellpose as a dock widget in Napari instead of a separate process"""
        if not CELLPOSE_AVAILABLE:
            self.filter_widget.add_to_chat(
                "[ERROR] Cellpose is not installed. Please install Cellpose to use this feature.")
            return

        # Check if the widget already exists
        if self.cellpose_widget is None:
            # Create the Cellpose widget
            self.cellpose_widget = CellposeNapariWidget(self.viewer)

            # Add it to Napari as a dock widget
            self.dock_widget = self.viewer.window.add_dock_widget(
                self.cellpose_widget,
                name="Cellpose",
                area="right"
            )

            self.filter_widget.add_to_chat(
                "[INFO] Cellpose interface launched in Napari")
        else:
            # If widget exists but was closed, reopen it
            self.viewer.window.add_dock_widget(
                self.cellpose_widget,
                name="Cellpose",
                area="right"
            )
            self.filter_widget.add_to_chat(
                "[INFO] Reopened Cellpose interface in Napari")
