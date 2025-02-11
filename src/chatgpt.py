
from os import remove
from pydantic import BaseModel
from typing import List, Union
from openai import OpenAI


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
