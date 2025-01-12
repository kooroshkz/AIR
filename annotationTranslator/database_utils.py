import sqlite3
import app_utils


def build_db_entry(img_filename: str, upload_dir: str) -> str:

    con = sqlite3.connect("database/database.db")
    cur = con.cursor()

    cur.execute(
        "INSERT INTO images (file_name, path) VALUES (?,?)",
        (img_filename, "placeholder"),
    )
    con.commit()

    res = cur.execute("SELECT MAX(image_id) FROM images")
    id_num = res.fetchone()[0]

    file_path = app_utils.build_data_dirs(upload_dir=upload_dir, id_num=id_num)

    res = cur.execute("UPDATE images SET path = ? WHERE image_id = ?", (id_num, file_path))

    return file_path
