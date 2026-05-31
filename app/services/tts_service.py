import edge_tts
import uuid
import os


AUDIO_DIR = "media/audio"

os.makedirs(AUDIO_DIR, exist_ok=True)


async def generate_tts(text: str):
    filename = f"{uuid.uuid4()}.mp3"

    output_path = os.path.join(
        AUDIO_DIR,
        filename
    )

    communicate = edge_tts.Communicate(
        text=text,
        voice="ru-RU-SvetlanaNeural"
    )

    await communicate.save(output_path)

    return f"/media/audio/{filename}"