from flask import Flask, render_template, request, jsonify, redirect
import os
from app_utils import *

app = Flask(__name__)

# set up uploads folder (where audio files get stored)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/")
def home():
    return render_template("base.html")

@app.route("/record")
def record():
    return render_template("record.html")

@app.post("/upload-data")
def upload_data():

    transcription_result = request.form.get('text')
    audio_file = request.files["audio"]
    image_file = request.files["image"]

    file_path = build_data_dirs(upload_dir = app.config["UPLOAD_FOLDER"])

    audio_file_path = os.path.join(file_path, str(audio_file.filename))
    image_file_path = os.path.join(file_path, str(image_file.filename))

    audio_file.save(audio_file_path)
    image_file.save(image_file_path)

    print("generating model response")
    annotation = get_model_response(transcription_result)
    print(annotation)

    return jsonify(
        {
            "status": "ok",
            "model-output": annotation,
        }
    )
