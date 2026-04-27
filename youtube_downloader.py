import yt_dlp
import whisper
import os

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
    model = whisper.load_model("base")  # you can use "small" or "large"
    result = model.transcribe(audio_path)
    return result["text"]


if __name__ == "__main__":
    path=download_youtube_audio("https://youtu.be/XYDQK5i0tmY?si=_Q2qLy_0v7jzk_MF")
    text=transcribe_audio(path)
    print(text)