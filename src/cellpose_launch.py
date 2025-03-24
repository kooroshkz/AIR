import subprocess
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
)


class CellposeLaunchPoint(QWidget):
    """
    Widget for launching a fork of Cellpose gui system
    all the cellpose code was modified by Luis Valero
    """

    def __init__(self, viewer, filter_widget):
        super().__init__()
        self.viewer = viewer
        self.filter_widget = filter_widget
        self.launch_btn = QPushButton("Launch CellPipe")  # the final stage
        self.launch_btn.setToolTip(
            "Launch a modified version of the Cellpose UI system\nUsing this, you can finalize your pipeline with a variety of segmentation models\nYou can also train your own model in a human-feedback loop")

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
        subprocess.run(["python", "-m", "cellpose"])
