from datetime import datetime
import os
import random
from moviepy import (
    VideoFileClip,
    concatenate_videoclips,
    AudioFileClip,
    CompositeAudioClip,
)
from mutagen.wave import WAVE
import soundfile as sf
from kokoro_onnx import Kokoro

# mastervidLoc = "Videos/masterVert.mp4"
mastervidLoc = "Videos/30minmastershort.mp4"
masteraudioLoc = "Audio/audio.wav"


def makeVideo(start, end, video, audio, timestamp):
    clip = VideoFileClip(video).subclipped(start, end)
    audio = AudioFileClip(audio)
    combined = concatenate_videoclips([clip])
    combined.audio = CompositeAudioClip([audio])
    combined.write_videofile(
        f"Upload/combined_{timestamp}.mp4",
        codec="h264_videotoolbox",
        audio_codec="aac",
        ffmpeg_params=["-b:v", "6000k", "-b:a", "192k"],
    )


def get_wav_duration(file_directory):
    audio = WAVE(file_directory)
    length = audio.info.length
    return length


def get_vid_duration(file_directory):
    clip = VideoFileClip(file_directory)
    return clip.duration


def runKororo(script_file):
    with open(script_file, "r") as f:
        text = f.read()
    kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
    samples, sample_rate = kokoro.create(
        text, voice="af_sarah", speed=1.0, lang="en-us"
    )
    sf.write("Audio/audio.wav", samples, sample_rate)


while True:
    with open("result.txt", "r") as f:
        content = f.read()
    chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
    if not chunks:
        print("result.txt is empty, all chunks processed.")
        break
    chunk = chunks[0]
    remaining = "\n\n".join(chunks[1:])
    with open("result.txt", "w") as f:
        f.write(remaining)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_file = f"transcriptions/timestamp_{timestamp}.txt"
    with open(script_file, "w") as f:
        f.write(chunk)
    print(f"Processing chunk: {chunk[:50]}...")
    print("Generating audio...")
    runKororo(script_file)
    audiolength = get_wav_duration(masteraudioLoc)
    vidlength = get_vid_duration(mastervidLoc)
    rand = random.randint(0, round(vidlength - audiolength - 1))
    makeVideo(rand, rand + audiolength, mastervidLoc, masteraudioLoc, timestamp)
    print(f"Done: Upload/combined_{timestamp}.mp4\n")

print("All chunks processed.")
