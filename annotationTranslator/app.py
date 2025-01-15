from flask import Flask, render_template, request, jsonify
import os
from app_utils import *
from database_utils import *
from logger import *

app = Flask(__name__)
logger = get_logger(__name__)

# set up uploads folder (where audio files get stored)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)



@app.route("/")
def home():
    """
    Home page for app
    TODO: decide on general layout and stuff
    """
    logger.info("Home page accessed.")
    return render_template("base.html")


@app.route("/record")
def record():
    """
    Main page for recording and annotation and interfacing with LLM
    """
    return render_template("record.html")


@app.post("/upload-data")
def upload_data():
    """
    Upload_data is the function that handles the data that the browser sends
    Also stores it in the database
    """
    logger.info("Recieved upload request.")
    status: str = "ok"
    message: str = "none"

    # first get the transcription
    transcription_result = request.form.get("text")

    # check for empty transcription
    if transcription_result is None or len(transcription_result) == 0:
        logger.warning("Missing required transcription in request.")
        status = "error"
        message = "empty transcription"

    if "audio" not in request.files or "image" not in request.files:
        logger.warning("Missing required files in request.")
        status = "error"
        message = "Missing files"

    audio_file = request.files["audio"]
    image_file = request.files["image"]

    logger.debug(f"Received transcription: {transcription_result}")
    logger.debug(f"Received audio file: {audio_file.filename}")
    logger.debug(f"Received image file: {image_file.filename}")

    # str(transcription_result) is just so that my LSP shuts up
    annotation_raw = get_model_response(str(transcription_result))

    # also creates the new folder inside of the main data folder
    # where audio, transcription, and image will get saved
    err = build_db_entry(image_file, audio_file, annotation_raw, app.config["UPLOAD_FOLDER"])

    if (err is not None):
        status = "error"
        message = "Error with creating database entries"

    logger.info("Data successfully processed and stored.")
    return jsonify(
        {
            "status": status,
            "message": message,
            "model-output": annotation_raw,
        }
    )
