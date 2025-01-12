import sqlite3
import app_utils
from werkzeug.datastructures import FileStorage
import os


def build_db_entry(
    image_file: FileStorage, audio_file: FileStorage, annotation: str, upload_dir: str
) -> None:

    con = sqlite3.connect("database/database.db")
    cur = con.cursor()

    # first GET THE PHOTO ID
    res = cur.execute("SELECT MAX(image_id) FROM images")
    id_num = res.fetchone()[0] + 1

    # build the directory to store them and then store them
    file_path = app_utils.build_data_dirs(upload_dir=upload_dir, id_num=id_num)

    audio_file_path = os.path.join(file_path, audio_file.filename)
    image_file_path = os.path.join(file_path, image_file.filename)

    audio_file.save(audio_file_path)
    image_file.save(image_file_path)
    with open(file_path + "/transcription.txt", "w") as f:
        f.write(annotation)

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
        (id_num, "transcription.txt", file_path + "/transcription.txt")
    )

    con.commit()
