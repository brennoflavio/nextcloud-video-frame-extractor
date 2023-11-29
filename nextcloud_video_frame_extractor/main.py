from webdav3.client import Client
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
from tempfile import NamedTemporaryFile
import subprocess
import sys
import sqlite3


load_dotenv()

def get_client():
    options = {
        "webdav_hostname": os.getenv("NEXTCLOUD_DAV_ENDPOINT"),
        "webdav_login": os.getenv("NEXTCLOUD_USERNAME"),
        "webdav_password": os.getenv("NEXTCLOUD_PASSWORD"),
    }
    client = Client(options)
    return client

def sanitize_path(path):
    path_to_strip = urlparse(os.getenv("NEXTCLOUD_DAV_ENDPOINT")).path
    return "/" + path.replace(path_to_strip, "")


def expand_directory(folder, client):
    files = []
    file_list = client.list(folder, get_info=True)

    for file in file_list:
        file["path"] = sanitize_path(file["path"])
        if file["path"] == folder:
            continue
        if file.get("isdir"):
            files.extend(expand_directory(file["path"], client))
        else:
            files.append(file)

    return [x for x in files if not x.get("isdir")]

def download_file(remote_path, local_path, client):
    return client.download_sync(remote_path=remote_path, local_path=local_path)

def check_file(remote_path, client):
    return client.check(remote_path)

def upload_file(remote_path, local_path, client):
    return client.upload_sync(remote_path=remote_path, local_path=local_path)

def get_file_extension(file_path):
    _, tail = os.path.split(file_path)
    _, ext = os.path.splitext(tail)
    return ext[1:]

def get_video_duration(file_path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path], capture_output=True)
    return float(result.stdout.decode().replace("\n", ""))

def extract_middle_frame(file_path, destination_path):
    duration = get_video_duration(file_path)
    frame = duration / 2.0
    subprocess.run(["ffmpeg", "-ss", str(frame), "-i", file_path, "-vframes", "1", "-y", destination_path])

def extract_first_frame(file_path, destination_path):
    duration = get_video_duration(file_path)
    frame = duration / 2.0
    subprocess.run(["ffmpeg", "-i", file_path, "-vframes", "1", "-y", destination_path])

def log_processed_video(remote_path):
    connection = sqlite3.connect(os.getenv("PROCESSED_VIDEO_DATABASE"))
    cursor = connection.cursor()
    cursor.execute("create table if not exists log(path text)")
    connection.commit()
    cursor.execute("insert into log(path) values (?)", (remote_path,))
    connection.commit()

def is_video_processed(remote_path):
    connection = sqlite3.connect(os.getenv("PROCESSED_VIDEO_DATABASE"))
    cursor = connection.cursor()
    cursor.execute("create table if not exists log(path text)")
    connection.commit()
    cursor.execute("select count(*) from log where path = ?", (remote_path,))
    result = cursor.fetchone()
    return bool(result[0])

def main():
    client = get_client()
    assert client

    folder = os.getenv("NEXTCLOUD_FOLDER")
    assert folder

    files = expand_directory(folder, client)
    files = [sanitize_path(x["path"]) for x in  files]
    files = [x for x in  files if get_file_extension(x) == "mp4"]

    for f in files:
        print(f)
        if is_video_processed(f):
            print("already processed, skipping")
            continue

        if not check_file(f, client):
            continue

        with NamedTemporaryFile("w+", suffix=".mp4") as video_file, NamedTemporaryFile("w+", suffix=".jpg") as image_file:
            download_file(f, video_file.name, client)
            extract_middle_frame(video_file.name, image_file.name)
            if not os.path.getsize(image_file.name):
                extract_first_frame(video_file.name, image_file.name)

            head, tail = os.path.split(f)
            filename, _ = os.path.splitext(tail)
            remote_path = os.path.join(head, f"{filename}_frame.jpg")

            upload_file(remote_path, image_file.name, client)
            log_processed_video(f)

if __name__ == "__main__":
    main()
