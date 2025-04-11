# src/stt.py

from tempfile import NamedTemporaryFile
from threading import Event, Thread
from os import remove
from dotenv import load_dotenv
from src.ai import GPT
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
        try:
            self.gpt = GPT(api_key=self.api_key, prompt="")
        except Exception as e:
            print(
                f"Error initializing GPT. Is the API key wrong? API KEY: {
                    self.api_key}, ERROR: {e}")

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
        try:
            wav_file = self._save_audio_to_temp_file()

            # Check audio duration before sending to Whisper API
            with wave.open(wav_file, 'rb') as wf:
                # Calculate duration in seconds
                duration = wf.getnframes() / wf.getframerate()

                # Whisper requires at least 0.1 seconds of audio
                if duration < 0.1:
                    remove(wav_file)
                    return "Audio too short to transcribe."

            transcript = self.gpt.whisper(wav_file)
            return transcript
        except Exception as e:
            print(f"Error during transcription: {e}")
            # Ensure temp file is removed in case of error
            try:
                if 'wav_file' in locals():
                    remove(wav_file)
            except BaseException:
                pass
            return f"Transcription error: {str(e)}"

    def start_streaming(self, callback=None, chunk_duration=3.0):
        """
        Begin streaming audio with real-time transcription.

        Args:
            callback: Function to call with transcription chunks as they become available
            chunk_duration: Duration in seconds for each audio chunk to process
        """
        if self._is_recording:
            return  # Already recording

        self._audio_data = []  # Clear previous recordings
        self._recording_event.clear()
        self._stream_callback = callback

        # Create a thread that will handle recording and streaming
        self._recording_thread = Thread(
            target=self._stream_loop,
            args=(callback, chunk_duration),
            daemon=True
        )
        self._recording_thread.start()
        self._is_recording = True
        print("Streaming started...")

    def _stream_loop(self, callback, chunk_duration):
        """
        Record audio and periodically transcribe chunks while continuing to record.
        """
        # Calculate number of frames in each chunk
        frames_per_chunk = int(self.sample_rate * chunk_duration)
        last_processed_frame = 0

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=np.int16,
            callback=self._audio_callback,
        ):
            while not self._recording_event.is_set():
                sd.sleep(100)  # Sleep briefly

                # Calculate total frames recorded so far
                if self._audio_data:
                    total_frames = sum(chunk.shape[0]
                                       for chunk in self._audio_data)

                    # If we have enough new frames for a chunk, process it
                    if total_frames - last_processed_frame >= frames_per_chunk:
                        # Process only new audio since last chunk
                        try:
                            # Save current chunk to temporary file
                            temp_file = self._save_chunk_to_temp_file(
                                last_processed_frame)

                            # Check audio duration
                            with wave.open(temp_file, 'rb') as wf:
                                duration = wf.getnframes() / wf.getframerate()

                                # Only transcribe if long enough
                                if duration >= 0.1:
                                    transcription = self.gpt.whisper(temp_file)
                                    if callback and transcription:
                                        callback(transcription)

                            # Clean up the temporary file
                            remove(temp_file)

                            # Update the last processed frame
                            last_processed_frame = total_frames

                        except Exception as e:
                            print(f"Streaming transcription error: {e}")

    def _save_chunk_to_temp_file(self, start_frame=0) -> str:
        """
        Save a chunk of the recorded audio data to a temporary WAV file.

        Args:
            start_frame: Starting frame index to process from

        Returns:
            Path to the temporary WAV file
        """
        if not self._audio_data:
            raise ValueError("No audio data recorded.")

        # Get full audio data as numpy array
        audio_np = np.concatenate(self._audio_data, axis=0)

        # Extract only the part we want (from start_frame to end)
        if start_frame > 0 and start_frame < audio_np.shape[0]:
            audio_np = audio_np[start_frame:]

        with NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            wav_file = tmp_file.name
            with wave.open(wav_file, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit PCM (2 bytes per sample)
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_np.tobytes())

        return wav_file

    def stop_streaming(self):
        """
        Stop the streaming process.
        """
        # Uses the same method as stop_recording
        self.stop_recording()
        print("Streaming stopped.")
