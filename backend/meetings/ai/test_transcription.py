import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

django.setup()


from meetings.ai.transcription import (
    transcribe_audio,
)


audio_path = "test_audio.webm"


with open(
    audio_path,
    "rb",
) as audio_file:

    audio_bytes = audio_file.read()


print("=" * 60)
print("WHISPER TRANSCRIPTION TEST")
print("=" * 60)


text = transcribe_audio(
    audio_bytes=audio_bytes,
    filename="test_audio.webm",
)


print()
print("TRANSCRIPTION:")
print(text)
print()
print("=" * 60)