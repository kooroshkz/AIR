# src/stt.py

from tempfile import NamedTemporaryFile
from threading import Event, Thread
from os import remove
from dotenv import load_dotenv
from src.chatgpt import GPT
import numpy as np
import sounddevice as sd
import wave


class STT:
    """
    A clean, class-based Speech-to-Text (STT) interface that records audio until
    a stop signal is received and transcribes it using OpenAI's Whisper API.
    """

    def __init__(
            self,
            api_key: str = None,
            sample_rate: int = 44100,
            channels: int = 1):
        load_dotenv()
        self.api_key = api_key
        self.sample_rate = sample_rate
        self.channels = channels

        # Internal variables for audio recording
        self._audio_data = []
        self._recording_event = Event()
        self._recording_thread = None
        self._is_recording = False

        # Create an instance of GPT for whisper functionality.
        self.gpt = GPT(api_key=self.api_key, prompt="")

    def _audio_callback(self, indata, frames, time, status):
        """
        Callback function used by the sounddevice InputStream to capture audio chunks.
        """
        self._audio_data.append(indata.copy())

    def start_recording(self):
        """
        Begin recording audio asynchronously. Recording will continue until stop_recording() is called.
        """
        if self._is_recording:
            return  # Already recording
        self._audio_data = []  # Clear previous recordings
        self._recording_event.clear()
        self._recording_thread = Thread(target=self._record_loop, daemon=True)
        self._recording_thread.start()
        self._is_recording = True
        print("Recording started...")

    def _record_loop(self):
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=np.int16,
            callback=self._audio_callback,
        ):
            while not self._recording_event.is_set():
                sd.sleep(100)

    def stop_recording(self):
        """
        Stop the recording process.
        """
        if not self._is_recording:
            return
        self._recording_event.set()
        if self._recording_thread is not None:
            self._recording_thread.join()
        self._is_recording = False
        print("Recording stopped.")

    def is_recording(self) -> bool:
        """
        Return whether recording is currently in progress.
        """
        return self._is_recording

    def _save_audio_to_temp_file(self) -> str:
        """
        Save the recorded audio data to a temporary WAV file.
        """
        if not self._audio_data:
            raise ValueError("No audio data recorded.")
        audio_np = np.concatenate(self._audio_data, axis=0)
        with NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            wav_file = tmp_file.name
            print(wav_file)
            with wave.open(wav_file, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit PCM (2 bytes per sample)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_np.tobytes())
        return wav_file

    def transcribe(self) -> str:
        """
        Transcribe the recorded audio using OpenAI's Whisper API.
        """
        wav_file = self._save_audio_to_temp_file()
        transcript = self.gpt.whisper(wav_file)
        return transcript
