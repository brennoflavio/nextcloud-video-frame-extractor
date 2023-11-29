# Nextcloud Video Frame Extractor
 
## Why?

Nextcloud app does not allow seeing video after video like images. Someties I just want to scroll
down and see a video preview, like a thumbmail.

### How?

This app scans a Nextcloud folder and uses ffmpeg to extract a frame of the video achieving that. It
iteracts with Nextcloud using WebDAV protocol.

#### Usage
Set up the environment variables in a `.env` file (see from `.env.example`):

```
NEXTCLOUD_DAV_ENDPOINT: Your Nextcloud WebDAV endpoint.
NEXTCLOUD_USERNAME: Your Nextcloud username.
NEXTCLOUD_PASSWORD: Your Nextcloud password.
NEXTCLOUD_FOLDER: The path of the Nextcloud folder you wish to convert files in.
PROCESSED_VIDEO_DATABASE: A sqlite database to avoid processing the same video over and over again
```

You can run the script with Poetry:
`poetry run nextcloud_video_frame_extractor/main.py`

#### Requirements

You need `ffmpeg` installed
