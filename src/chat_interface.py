from os import getenv
from openai import OpenAI
import numpy as np
import asyncio
from threading import Thread
from qtpy.QtCore import QEvent, Qt
from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLineEdit,
    QTextEdit
)
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
    apply_ridge_detection,
)
from .ai import GPT, ElevenLabsTTS
from .utils import run_tts_in_thread
# The exception handles the headless CICD testing
try:
    from .stt import STT
except OSError:
    STT = None

class ChatWidget(QWidget):
    """
    Multi-modal chat widget supporting text and speech interaction.
    Speech is triggered by holding the spacebar. (Not anymore, todo?)
    """

    def __init__(self, viewer, filter_widget):
        """
        Initialize the chat widget, available commands, and UI.
        """
        super().__init__()
        self.viewer = viewer
        self.filter_widget = filter_widget  # Reference to an ImageFilterWidget, if needed
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
            "ridge_detection": apply_ridge_detection,
        }

        voice_settings = {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 1,
            "use_speaker_boost": True
        }
        voice_id = "EXAVITQu4vr4xnSDxMaL" # sarah
        model_id = "eleven_flash_v2_5"
        generation_url = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model_id}"

        AI_PROMPT = getenv("AI_PROMPT")
        OPENAI_API_KEY = getenv("OPENAI_API_KEY")
        ELEVENLABS_API_KEY = getenv("ELEVENLABS_API_KEY")

        self.ai_system_prompt = AI_PROMPT
        self.Chat = GPT(api_key=OPENAI_API_KEY, prompt=AI_PROMPT)
        self.Speak = ElevenLabsTTS(gen_uri=generation_url, api_key=ELEVENLABS_API_KEY, voice_settings=voice_settings)

        if STT is not None:
            self.stt = STT(api_key=OPENAI_API_KEY)

    def setup_ui(self):
        """Configure the widget's user interface."""
        layout = QVBoxLayout()

        # Chat history text area
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

        # Horizontal layout for text input, send button, and record button
        input_layout = QHBoxLayout()

        # Input field for text messages
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(
            "Enter your image processing request...")
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
        input_layout.addWidget(self.input_field)

        # Send button for text input
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
        input_layout.addWidget(self.send_button)

        # Record button for audio input (press-and-hold)
        self.record_button = QPushButton("Hold to Record")
        self.record_button.setStyleSheet(
            """
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            """
        )
        # When pressed, start recording; when released, stop and process the
        # audio.
        self.record_button.pressed.connect(self.start_audio_recording)
        self.record_button.released.connect(self.stop_audio_recording)
        input_layout.addWidget(self.record_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

    def start_audio_recording(self):
        """Start audio recording and update UI to indicate recording state."""
        self.record_button.setText("Recording...")
        self.stt.start_recording()

    def stop_audio_recording(self):
        """
        Stop audio recording, transcribe the audio, and process the transcript.
        Updates the UI and sends the transcribed text to the GPT API.
        """
        self.record_button.setText("Transcribing...")
        self.stt.stop_recording()
        transcript = self.stt.transcribe()
        self.chat_history.append(f"[👤] User: <i>{transcript}</i>")

        try:
            response_text, action = self.Chat.say(transcript)
            if response_text:
                self.add_to_chat(f'[🤖] <b>{response_text}</b>')
                Thread(target=run_tts_in_thread, args=(self.Speak.stream_tts, response_text), daemon=True).start()
            if action:
                self.add_to_chat(f'[⚙️] <b>{self.format_action(action)}</b>')
                self.execute_command(action)
        except Exception as e:
            self.add_to_chat("[⚠️] Error: " + str(e))

        self.record_button.setText("Hold to Record")

    def process_input(self):
        """
        Handles User to AI interaction
        """
        user_input = self.input_field.text()
        if not user_input:
            return

        self.add_to_chat(f'[👤] User: <i>{user_input}</i>')
        self.input_field.clear()

        # Process with LLM
        try:
            response_text, action = self.Chat.say(user_input)
            if response_text:
                self.add_to_chat(f'[🤖] <b>{response_text}</b>')
                Thread(target=run_tts_in_thread, args=(self.Speak.stream_tts, response_text), daemon=True).start()
            if action:
                self.add_to_chat(f'[⚙️] <b>{self.format_action(action)}</b>')
                self.execute_command(action)
        except Exception as e:
            self.add_to_chat("[⚠️] Error: " + str(e))

    def format_action(self, action):
        """
        str formating
        """
        return ", ".join([
            f"{act.action_name} {','.join(str(it) for it in act.action_args)}" for act in action
        ])

    def add_to_chat(self, message):
        """
        Appends to the chat a message
        """
        self.chat_history.append(message)

    def change_layer(self, curr_layer, filtered_array, filter_name):
        """
        Switches the current layer to the newest filtered layer
        """
        self.filter_widget._push_to_history(curr_layer)
        if hasattr(filtered_array, "__array__"):
            filtered_array = np.asarray(filtered_array)
        elif not isinstance(filtered_array, np.ndarray):
            filtered_array = np.array(filtered_array)

        # Create new layer with descriptive name and add to napari viewer
        new_layer_name = f"{curr_layer.name} | {filter_name}"
        self.viewer.add_image(filtered_array, name=new_layer_name)

    def execute_command(self, command):
        """
        Executes a command from the LLM
        """
        # print(command)

        for action in command:

            funct = action.action_name
            param = action.action_args

            layer = self.filter_widget._get_current_layer()
            img = self.filter_widget.original_data.copy()

            if param != []:
                filtered_array = self.available_commands[funct](
                    img, param[0])
            else:
                filtered_array = self.available_commands[funct](img)
            self.change_layer(layer, filtered_array, funct.title())
            if param == []:
                self.filter_widget._push_to_history(layer)
        return

        # OLD system
        # command = command.lower().strip()
        # parts = command.split()
        # cmd_name = parts[0]

        # # Handle saturation separately since it needs an integer value
        # # Get current layer
        # layer = self.filter_widget._get_current_layer()
        # img = self.filter_widget.original_data.copy()

        # # Handle commands with parameters
        # if len(parts) > 1:
        #     try:
        #         value = float(parts[1])
        #         if cmd_name in ["blur", "contrast", "saturation", "sharpen"]:
        #             filtered_array = self.available_commands[cmd_name](img, value)
        #             self.change_layer(layer, filtered_array, cmd_name.title())
        #             # self.add_to_chat(f"Executed: {cmd_name} with value {value}")
        #             return
        #     except (IndexError, ValueError):
        #         self.filter_widget.add_to_chat(
        #             f"Error: {cmd_name} requires a valid numeric value"
        #         )
        #         return

        # # Handle commands without parameters
        # if cmd_name in self.available_commands:
        #     try:
        #         filtered_array = self.available_commands[cmd_name](img)
        #         self.change_layer(layer, filtered_array, cmd_name.title())
        #         # self.add_to_chat(f"Executed: {cmd_name}")
        #         self.filter_widget._push_to_history(layer)
        #         return
        #     except Exception as e:
        #         self.add_to_chat(f"Error executing {cmd_name}: {str(e)}")
        #         return

        # self.add_to_chat("I did not quite catch that one.")
