from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, 
    QPushButton, QLineEdit
)
from qtpy.QtCore import Qt
from openai import OpenAI
import os
import numpy as np
from .napari_image_filters import (
    apply_gaussian_blur, apply_contrast_enhancement,
    apply_texture_analysis, apply_adaptive_threshold,
    apply_sharpening
)


class ChatWidget(QWidget):
    def __init__(self, viewer, filter_widget):
        super().__init__()
        self.viewer = viewer
        self.filter_widget = filter_widget  # Store reference to ImageFilterWidget
        self.setup_ui()
        self.available_commands = {
            'grayscale': self.filter_widget._apply_grayscale,
            'saturation': self.filter_widget._update_saturation,
            'edge_enhance': self.filter_widget._apply_edge_enhance,
            'edge_detection': self.filter_widget._apply_edge_detection,
            'blur': apply_gaussian_blur,
            'contrast': apply_contrast_enhancement,
            'texture': apply_texture_analysis,
            'threshold': apply_adaptive_threshold,
            'sharpen': apply_sharpening,
        }

        # Initialize your LLM client here
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )

    def setup_ui(self):
        """Configure the widget's user interface."""
        layout = QVBoxLayout()

        # Chat history with improved styling
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                padding: 5px;
            }
        """)
        layout.addWidget(self.chat_history)

        # Input field with placeholder and styling
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter your image processing request...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
        """)
        self.input_field.returnPressed.connect(self.process_input)
        layout.addWidget(self.input_field)

        # Send button with styling
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0366d6;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0255b3;
            }
        """)
        self.send_button.clicked.connect(self.process_input)
        layout.addWidget(self.send_button)

        self.setLayout(layout)


    def process_input(self):
        user_input = self.input_field.text()
        if not user_input:
            return

        self.add_to_chat("User: " + user_input)
        self.input_field.clear()

        # Process with LLM
        try:
            response = self.get_llm_response(user_input)
            self.add_to_chat("Assistant: {}".format(response))
            self.execute_command(response)
        except Exception as e:
            self.add_to_chat("Error: " + str(e))

    def add_to_chat(self, message):
        self.chat_history.append(message)

    def get_llm_response(self, user_input):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """
                You are an image processing assistant. Convert user requests into specific commands.
                Available commands and their formats:
                - grayscale: Convert image to grayscale
                - saturation <value>: Adjust image saturation (integer value between 0 and 200, where the default saturation is 100)
                - edge_enhance: Enhance edges in the image
                - edge_detection: Detect edges in the image
                - blur <radius>: Apply Gaussian blur (radius between 0.1 and 10.0)
                - contrast <factor>: Enhance contrast (factor between 0.1 and 3.0, default is 1.5)
                - texture: Analyze image texture
                - threshold: Apply adaptive thresholding
                - sharpen <strength>: Sharpen the image (strength between 0.1 and 2.0)

                Respond ONLY with the command and any necessary parameters.
                Examples:
                - blur 2.5
                - contrast 1.8
                - sharpen 1.2
                - grayscale
                - saturation 100(can be between 0-200)
                - edge_enhance
                - edge_detection
                """},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content

    def change_layer(self, curr_layer, filtered_array):
        self.filter_widget._push_to_history(curr_layer)
        if hasattr(filtered_array, '__array__'):
            filtered_array = np.asarray(filtered_array)
        elif not isinstance(filtered_array, np.ndarray):
            filtered_array = np.array(filtered_array)

        curr_layer.data = filtered_array


    def execute_command(self, command):
        command = command.lower().strip()
        parts = command.split()
        cmd_name = parts[0]

        # Handle saturation separately since it needs an integer value
        # Get current layer
        layer = self.filter_widget._get_current_layer()
        img = self.filter_widget.original_data.copy()
        

        if 'saturation' in command:
            try:
                value = int(command.split()[-1])
                filtered_array = self.available_commands['saturation'](value)
                self.change_layer(layer, filtered_array)
                self.add_to_chat(f"Executed: saturation with value {value}")
                return
            except (IndexError, ValueError) as e:
                print(e)
                self.filter_widget.add_to_chat("Error: Saturation requires a numeric value between 0-200")
                return


        # Handle commands with parameters
        if len(parts) > 1:
            try:
                value = float(parts[1])
                if cmd_name in ['blur', 'contrast', 'saturation', 'sharpen']:
                    filtered_array = self.available_commands[cmd_name](img, value)
                    self.change_layer(layer, filtered_array)
                    self.add_to_chat(f"Executed: {cmd_name} with value {value}")
                    return
            except (IndexError, ValueError):
                self.filter_widget.add_to_chat(f"Error: {cmd_name} requires a valid numeric value")
                return

        # Handle commands without parameters
        if cmd_name in self.available_commands:
            try:
                filtered_array = self.available_commands[cmd_name](img)
                self.change_layer(layer, filtered_array)
                self.add_to_chat(f"Executed: {cmd_name}")
                self.filter_widget._push_to_history(layer)
                return
            except Exception as e:
                self.filter_widget.add_to_chat(f"Error executing {cmd_name}: {str(e)}")
                return

        self.add_to_chat("I did not quite catch that one.")
