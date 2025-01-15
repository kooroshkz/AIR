import sqlite3
import app_utils
from werkzeug.datastructures import FileStorage
import os
from logger import *

logger = get_logger(__name__)

def build_db_entry(
    image_file: FileStorage, audio_file: FileStorage, annotation: str, upload_dir: str
) -> sqlite3.Error | OSError | IOError | None:
    try:
        con = sqlite3.connect("database/database.db")
        cur = con.cursor()
        logger.info("Connected to database.") 
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        return e

    try:

        # first GET THE PHOTO ID
        res = cur.execute("SELECT MAX(image_id) FROM images")
        id_num = (res.fetchone()[0] or 0) + 1

        logger.debug(f"New image ID: {id_num}")

    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve max image_id: {e}")
        con.close()
        return e

    try:

        # build the directory to store them and then store them
        file_path = app_utils.build_data_dirs(upload_dir=upload_dir, id_num=id_num)
        #str()s here are also so my LSP shuts up
        audio_file_path = os.path.join(str(file_path), str(audio_file.filename))
        image_file_path = os.path.join(str(file_path), str(image_file.filename))

        audio_file.save(audio_file_path)
        image_file.save(image_file_path)

        with open(file_path + "/transcription.txt", "w") as f:
            f.write(annotation)

        logger.info(f"Files saved successfully at {file_path}")

    except (OSError, IOError) as e:
        logger.error(f"File handling error: {e}")
        con.close()
        return e


    try:
        # now that we have all the paths, add all the DB entries
        # add image entry first
        cur.execute(
            "INSERT INTO images (file_name, path) VALUES (?,?)",
            (image_file.filename, image_file_path),
        )
        # add audio entry
        cur.execute(
            "INSERT INTO audio (image_id, file_name, path, transcription, audio_format) VALUES (?, ?, ?, ?, ?)",
            (id_num, audio_file.filename, audio_file_path, "-", "wav"),
        )
        # add annotation entry
        cur.execute(
            "INSERT INTO annotations (image_id, file_name, path) VALUES (?, ?, ?)",
            (id_num, "transcription.txt", file_path + "transcription.txt"),
        )

        con.commit()
        logger.info(f"Database entry created successfully for image_id {id_num}")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        con.rollback()
        return e

    return None
