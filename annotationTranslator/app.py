from flask import Flask, render_template, request, jsonify
import os
#from transformers import pipeline
import requests

app = Flask(__name__)

upload_folder = "uploads"
app.config["upload_folder"] = upload_folder
os.makedirs(upload_folder, exist_ok=True)

API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"
headers = {"Authorization": "Bearer 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"}

@app.route("/")
def home():
    return render_template("base.html")


@app.route("/record")
def record():
    return render_template("record.html")


# post request for uploading the audio blob handler
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


# post request for uploading the transcribed audio handler
@app.post("/upload-transcription")
def upload_transcription():

    data = request.get_json()
    text = data.get("text", "")

    payload = {
        "inputs": text,
    }

    response = requests.post(API_URL, headers=headers, json = payload) 

    print(f"Received text: {text}")
    print(f"model output: {response.json()}")


    return jsonify(
        {
            "status": "success",
            "model-output": response.json(),
        }
    )
