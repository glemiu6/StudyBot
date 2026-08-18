from youtube_downloader import download_youtube_audio, transcribe_audio, extract_video_id
from pathlib import Path
import os


class VideoLoader:
    """
    VideoLoader: Downloads and transcribes YouTube videos into text with caching.\n

    This class provides a simple interface to:\n
        1. Check if the video has already been processed.
        2. Download audio from a video using 'download_youtube_audio'.
        3. Transcribe audio to text using 'transcribe_audio'.
        4. Save transcripts in a local cache folder to avoid re-processing.
        5. Clean up temporary audio files automatically.

    Usage Examples:
        loader=VideoLoader(output_dir="video_cache")
        result=loader.process_video("https://www.youtube.com/watch?v=ABC123") \n
        print(result["text"])

    Attributes:
        output_dir (Path): Directory where transcripts are stored
    """

    def __init__(self, output_dir="video_cache"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def _video_already_processed(self, video_id: str):
        """
        Checks if a transcript already exists for a given video.

        Args:
            video_id (str): YouTube video ID

        Returns:
            tuple: (exists: bool, txt_path: Path)
        """
        txt_path = self.output_dir / f"{video_id}.txt"
        return txt_path.exists(), txt_path

    def download_audio(self, url: str):
        """Downloads audio from a YouTube URL. Returns path to downloaded audio file."""
        return download_youtube_audio(url)

    def transcribe(self, audio_path):
        """Transcribes audio to text."""
        return transcribe_audio(audio_path)

    def process_video(self, url) -> dict[str, str | dict]:
        """
        Process a video by downloading its audio, transcribing it, and saving the transcript.

        Args:
            url (str): YouTube video URL.

        Returns:
            dict: {"text": str, "metadatas": dict}
                metadatas uses "file_id" (not "video_id") so it lines up with
                FileLoader's convention and with BasePipeline._is_ingested()/
                list_files(), which key off "file_id".
        """
        video_id = extract_video_id(url)
        exists, txt_path = self._video_already_processed(video_id)

        metadata = {
            "file_id": video_id,
            "file_name": f"{video_id}.txt",
            "video_id": video_id,
            "url": url,
            "source": url,
        }

        if exists:
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()
            return {"text": text, "metadatas": metadata}

        audio_path = self.download_audio(url)
        text = self.transcribe(audio_path)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        if os.path.exists(audio_path):
            os.remove(audio_path)

        return {"text": text, "metadatas": metadata}