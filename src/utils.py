from qtpy.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)

class DropdownPopup(QDialog):
    """a menu that popsup, for when selecting the pipeline to apply the final postprocessing model finetuning"""

    def __init__(self, options):
        super().__init__()
        self.setWindowTitle("Select an Option")

        # Create dropdown (combo box)
        self.combo_box = QComboBox()
        self.combo_box.addItems(options)

        # Add a label and dropdown to layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Choose an option:"))
        layout.addWidget(self.combo_box)

        # Add OK & Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_selected_option(self):
        """Returns the selected option when dialog is accepted."""
        return self.combo_box.currentText()
