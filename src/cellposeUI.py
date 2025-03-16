from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
)

class CellposeUILauncher(QWidget):
    """
    Widget for launching the cellpose UI
    """

    def __init__(self, viewer, filter_widget):
        super().__init__()
        self.viewer = viewer
        self.filter_widget = filter_widget

        self.launch_btn = QPushButton("Lauch Cellpose UI")

        self.setup_ui()

    def setup_ui(self):
        """Configure the widget's user interface."""

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
        self.launch_btn.clicked.connect(self._launch_cellpose_ui)

        layout = QHBoxLayout()
        layout.addWidget(self.launch_btn)

        self.setLayout(layout)

    def _launch_cellpose_ui(self):
        try:
            self.filter_widget.chat_widget.add_to_chat("[Status] Launching cellpose UI")
            import subprocess
            subprocess.Popen(["python", "-m", "cellpose"])
            import cellpose

        except Exception as e:
            self.filter_widget.chat_widget.add_to_chat("[Error] Could not launch cellpose UI")
            self.filter_widget.chat_widget.add_to_chat(f"[Message] {e}")
