import os
from qtpy.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLineEdit
from openai import OpenAI
import numpy as np
from .napari_image_filters import (
    apply_grayscale,
    apply_saturation,
    apply_edge_enhance,
    apply_edge_detection,
    apply_gaussian_blur,
    apply_contrast_enhancement,
    apply_texture_analysis,
    apply_adaptive_threshold,
    apply_sharpening,
)


class ChatWidget(QWidget):
    """
    Multi-modal chat widget which is will support both text and speech interaction
    """

    def __init__(self, viewer, filter_widget):
        """
        Initialize everything. Including what commands are possible to use,
        and how the chatUI should look like.
        """
        super().__init__()
        self.viewer = viewer
        self.filter_widget = filter_widget  # Store reference to ImageFilterWidget
        self.setup_ui()
        self.available_commands = {
            "grayscale": apply_grayscale,
            "saturation": apply_saturation,
            "edge_enhance": apply_edge_enhance,
            "edge_detection": apply_edge_detection,
            "blur": apply_gaussian_blur,
            "contrast": apply_contrast_enhancement,
            "texture": apply_texture_analysis,
            "threshold": apply_adaptive_threshold,
            "sharpen": apply_sharpening,
        }
        self.ai_system_prompt = os.getenv("AI_PROMPT")
        # Initialize your LLM client here
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def setup_ui(self):
        """Configure the widget's user interface."""
        layout = QVBoxLayout()

        # Chat history with improved styling
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #cccccc;
                padding: 5px;
            }
        """
        )
        layout.addWidget(self.chat_history)

        # Input field with placeholder and styling
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter your image processing request...")
        self.input_field.setStyleSheet(
            """
            QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
        """
        )
        self.input_field.returnPressed.connect(self.process_input)
        layout.addWidget(self.input_field)

        # Send button with styling
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet(
            """
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
        """
        )
        self.send_button.clicked.connect(self.process_input)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def process_input(self):
        """
        Handles User to AI interaction
        """
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
        """
        Appends to the chat a message
        """
        self.chat_history.append(message)

    def get_llm_response(self, user_input):
        """
        Fetches the response from the LLM model with a given system prompt
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.ai_system_prompt},
                {"role": "user", "content": user_input},
            ],
        )
        return response.choices[0].message.content

    def change_layer(self, curr_layer, filtered_array):
        """
        Switches the current layer to the newest filtered layer
        """
        self.filter_widget._push_to_history(curr_layer)
        if hasattr(filtered_array, "__array__"):
            filtered_array = np.asarray(filtered_array)
        elif not isinstance(filtered_array, np.ndarray):
            filtered_array = np.array(filtered_array)

        curr_layer.data = filtered_array

    def execute_command(self, command):
        """
        Executes a command from the LLM
        """
        command = command.lower().strip()
        parts = command.split()
        cmd_name = parts[0]

        # Handle saturation separately since it needs an integer value
        # Get current layer
        layer = self.filter_widget._get_current_layer()
        img = self.filter_widget.original_data.copy()

        # Handle commands with parameters
        if len(parts) > 1:
            try:
                value = float(parts[1])
                if cmd_name in ["blur", "contrast", "saturation", "sharpen"]:
                    filtered_array = self.available_commands[cmd_name](img, value)
                    self.change_layer(layer, filtered_array)
                    self.add_to_chat(f"Executed: {cmd_name} with value {value}")
                    return
            except (IndexError, ValueError):
                self.filter_widget.add_to_chat(
                    f"Error: {cmd_name} requires a valid numeric value"
                )
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
                self.add_to_chat(f"Error executing {cmd_name}: {str(e)}")
                return

        self.add_to_chat("I did not quite catch that one.")
