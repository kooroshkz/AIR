from typing import Callable, List, Tuple
from PyQt5.QtWidgets import (
    QVBoxLayout, QPushButton, QDialog
)


class ImageFiltersUI(QDialog):
    def __init__(self, filter_buttons: List[Tuple[str, Callable]]):
        super().__init__()
        self.setWindowTitle("Image Filters")
        self.setGeometry(200, 200, 200, 200)

        # Grid layout for buttons
        layout = QVBoxLayout()
        self.setStyleSheet(
            """
        background-color: #808080;
        """
        )

        for name, method in filter_buttons:
            btn = QPushButton(name)
            btn.setStyleSheet(
                "background-color: #4A90E2; color: black; font-size: 16px; padding: 5px;"
            )
            btn.clicked.connect(method)
            layout.addWidget(btn)

        self.setLayout(layout)
