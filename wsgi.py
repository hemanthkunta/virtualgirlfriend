import os


for directory in ("audio_input", "audio_output", "processed_videos"):
    os.makedirs(directory, exist_ok=True)


from app import app  # noqa: E402
