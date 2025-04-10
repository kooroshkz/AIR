from os import remove
from pydantic import BaseModel
from typing import List, Union
from openai import OpenAI
import asyncio
from json import dumps, loads
from base64 import b64decode
import websockets


class ActionModel(BaseModel):
    action_name: str
    action_args: List[Union[str, int, bool]]


class ActionChainModel(BaseModel):
    response_text: str  # Note: Fixed typo "reponse_text" -> "response_text"
    action: List[ActionModel]


class GPT:
    def __init__(self, api_key: str, prompt: str = ""):
        self.client = OpenAI(api_key=api_key)
        self.messages = [{"role": "system", "content": prompt}]

    def say(self, message: str):
        self.messages.append({"role": "user", "content": message})
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=self.messages,
            response_format=ActionChainModel
        )
        event = response.choices[0].message.parsed
        print(event)
        return event.response_text, event.action

    def whisper(self, file_path: str) -> str:
        """
        Transcribe an audio file using OpenAI's Whisper API.
        After transcription, the temporary file is removed.
        """
        with open(file_path, "rb") as f:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        remove(file_path)
        return transcript.text


class ElevenLabsTTS:
    def __init__(self, gen_uri, api_key, voice_settings):
        self.gen_uri = gen_uri
        self.api_key = api_key
        self.voice_settings = voice_settings

    async def stream_tts(self, text: str):
        """Open a websocket, stream text in small chunks, and play audio concurrently."""
        async with websockets.connect(self.gen_uri) as ws:
            # Initialization message to prepare the connection.
            init_msg = {
                "text": " ",
                "voice_settings": self.voice_settings,
                "xi_api_key": self.api_key
            }
            await ws.send(dumps(init_msg))
            # Start the audio playback concurrently.
            audio_task = asyncio.create_task(self.play_audio(ws))

            # Send the text in small chunks.
            chunk_size = 50  # Adjust chunk size as desired.
            for i in range(0, len(text), chunk_size):
                await ws.send(dumps({"text": text[i:i + chunk_size]}))
                # Allows ElevenLabs to process and stream audio.
                await asyncio.sleep(0.1)

            # Signal the end of the text stream.
            await ws.send(dumps({"text": ""}))
            await audio_task

    async def play_audio(self, ws):
        """Continuously receives audio chunks and pipes them to mpv for playback."""
        # install mpv if u dont have it
        proc = await asyncio.create_subprocess_exec(
            "mpv", "--no-cache", "--no-terminal", "--", "fd://0",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        while True:
            message = loads(await ws.recv())
            # Decode and forward audio if available.
            if (audio_data := message.get("audio")):
                proc.stdin.write(b64decode(audio_data))
                await proc.stdin.drain()
            if message.get("isFinal"):
                break
        proc.stdin.close()
        await proc.wait()
