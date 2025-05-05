from TTS.api import TTS
from pydub import AudioSegment
from pydub.playback import play
from functools import lru_cache

@lru_cache(maxsize=1)

def text_to_speech(text: str, output_file: str = "output.wav", speaker_id: str = "p232", pitch_shift: int = 1, speed_factor: float = 1):
    # Initialize the TTS model with the VCTK dataset
    # 1) Generate the raw TTS output
    model_name = "tts_models/en/vctk/vits"
    tts = TTS(model_name)
    temp_file = "temp.wav"
    tts.tts_to_file(text=text, file_path=temp_file, speaker=speaker_id)

    # 2) Load it with pydub
    audio = AudioSegment.from_file(temp_file)

 #4) Speed it up
    if speed_factor != 1:
        audio = audio.speedup(playback_speed=speed_factor)

    # 5) Export your final file
    audio.export(output_file, format="wav")
    print(f"🚀 Saved sped-up audio as {output_file}")