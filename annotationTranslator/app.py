from flask import Flask, render_template, request, jsonify, redirect
import os
from app_utils import *
from database_utils import *

app = Flask(__name__)

# set up uploads folder (where audio files get stored)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

"""
Home page for app
TODO: decide on general layout and stuff
"""
@app.route("/")
def home():
    return render_template("base.html")

"""
Main page for recording and annotation and interfacing with LLM
"""
@app.route("/record")
def record():
    return render_template("record.html")

"""
Upload_data is the function that handles the data that the browser sends
Also stores it in the database
"""
@app.post("/upload-data")
def upload_data():

    transcription_result = request.form.get('text')
    audio_file = request.files["audio"]
    image_file = request.files["image"]

    audio_filename : str = str(audio_file.filename)
    image_filename : str = str(image_file.filename)

    #also creates the new folder inside of the main data folder where audio, transcription, and image will get saved
    file_path = build_db_entry(image_filename, app.config["UPLOAD_FOLDER"])

    print(file_path)

    audio_file_path = os.path.join(file_path, audio_filename)
    image_file_path = os.path.join(file_path, image_filename)

    audio_file.save(audio_file_path)
    image_file.save(image_file_path)

    annotation = get_model_response(transcription_result)

    with open(file_path + "/transcription.txt", "w") as f:
        f.write(annotation[0]['generated_text'])

    return jsonify(
        {
            "status": "ok",
            "model-output": annotation,
        }
    )
