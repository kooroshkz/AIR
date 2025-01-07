from flask import Flask, render_template, request, jsonify
import os
from app_utils import *

# from transformers import pipeline
import requests

app = Flask(__name__)

#set up uploads folder (where audio files get stored)
upload_folder = "uploads"
app.config["upload_folder"] = upload_folder
os.makedirs(upload_folder, exist_ok=True)


#Hugging face API key
API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"
headers = {"Authorization": "Bearer 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"}


""" 
/ is the first page where users get sent to
    for now it is temporary, it is only here for in case any extra functionalities need to get added
"""
@app.route("/")
def home():
    return render_template("base.html")

"""
record() handles the actual recording HTML page
"""
@app.route("/record")
def record():
    return render_template("record.html")


"""
handles the audio file uploaded by the user
"""
@app.post("/upload-audio")
def upload_audio():

    # save the file
    result = request.files["audio"]
    file_path = os.path.join(app.config["upload_folder"], result.filename)
    result.save(file_path)

    return jsonify(
        {
            "status": "success",
        }
    )


"""
handles the model and returns its response
"""
@app.post("/upload-transcription")
def upload_transcription():

    data = request.get_json()
    text = data.get("text", "")

    payload = {
        "inputs": text,
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    model_output = response_to_output_raw(response)

    if (type(model_output) == dict):
        raise ValueError(f"Error: unrecognized return from LLM: {model_output}")

    #clean the response to return
    response_clean = response.json()
    response_clean[0]["generated_text"] = clean_response(model_output, text)

    return jsonify(
        {
            "status": "success",
            # model-output wants the json (not decoded), the decoding happens on the client-side
            "model-output": response_clean,
        }
    )
