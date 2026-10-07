import os
import tempfile

from groq import Groq


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def transcribe_audio(
    audio_bytes,
    filename="audio.webm",
):
    """
    Send an audio chunk to Groq Whisper
    and return the transcription text.
    """

    if not audio_bytes:
        return ""


    with tempfile.NamedTemporaryFile(
        suffix=".webm",
        delete=False,
    ) as temp_file:

        temp_file.write(audio_bytes)

        temp_file_path = temp_file.name


    try:

        with open(
            temp_file_path,
            "rb",
        ) as audio_file:

            transcription = client.audio.transcriptions.create(
                file=(
                    filename,
                    audio_file.read(),
                ),
                model="whisper-large-v3-turbo",
                response_format="json",
                temperature=0,
            )


        return transcription.text.strip()


    finally:

        os.remove(
            temp_file_path
        )