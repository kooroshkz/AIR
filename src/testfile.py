from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QDialog, QGridLayout
)


class ExtraButtonsPopup(QDialog):
    """ Pop-up window with extra buttons. """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extra Buttons")
        self.setGeometry(200, 200, 200, 200)

        # Grid layout for buttons
        layout = QGridLayout()

        # Create buttons dynamically
        for i in range(1, 7):
            button = QPushButton(f"Button {i}")
            button.clicked.connect(lambda _, num=i: self.button_clicked(num))
            layout.addWidget(button, (i - 1) // 2, (i - 1) % 2)

        self.setLayout(layout)

    def button_clicked(self, number):
        """ Print button number when clicked. """
        print(f"Button {number} clicked!")


class MainApp(QWidget):
    """ Main application window. """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Main button that opens the popup
        open_popup_button = QPushButton("Open Extra Buttons")
        open_popup_button.clicked.connect(self.open_popup)

        layout.addWidget(open_popup_button)
        self.setLayout(layout)
        self.setWindowTitle("Popup Button Demo")

    def open_popup(self):
        """ Show the popup window with extra buttons. """
        popup = ExtraButtonsPopup()
        popup.exec_()


app = QApplication([])
window = MainApp()
window.show()
app.exec_()

