FROM python:3.10

WORKDIR /app

RUN apt-get update -y
RUN apt-get install ffmpeg -y

COPY pyproject.toml /app/pyproject.toml

RUN pip install poetry
RUN pip install poetry-plugin-export

RUN poetry export -f requirements.txt --output requirements.txt

RUN pip install -r requirements.txt

COPY ./nextcloud_video_frame_extractor .
