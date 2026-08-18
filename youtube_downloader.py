import os
from urllib.parse import urlparse, parse_qs

import yt_dlp
import whisper

_whisper_model = None  # cached across calls so we don't reload it every transcription


def extract_video_id(url: str) -> str:
    """
    Extract a stable YouTube video ID from either a short (youtu.be/XXXX)
    or long (youtube.com/watch?v=XXXX) URL. Falls back to the raw URL if
    neither pattern matches, so callers never crash on an unexpected format.
    """
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")
    if parsed.hostname and "youtube.com" in parsed.hostname:
        video_id = parse_qs(parsed.query).get("v")
        if video_id:
            return video_id[0]
    return url


def download_youtube_audio(youtube_url, output_path="temp_audio.mp3"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path.replace('.mp3', ''),
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([youtube_url])
        except Exception as e:
            print(f"[WARNING] Could not download youtube audio: {e}")
            raise
    downloaded_path = output_path.replace('.mp3', '') + ".mp3"
    if os.path.exists(downloaded_path):
        os.rename(downloaded_path, output_path)
    else:
        raise FileNotFoundError(f"Expected audio file not found: {downloaded_path}")
    return output_path


def transcribe_audio(audio_path):
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model("base")  # you can use "small" or "large"
    result = _whisper_model.transcribe(audio_path)
    return result["text"]


if __name__ == "__main__":
    test_url = "https://youtu.be/XYDQK5i0tmY?si=_Q2qLy_0v7jzk_MF"
    print(extract_video_id(test_url))
    path = download_youtube_audio(test_url)
    text = transcribe_audio(path)
    print(text)