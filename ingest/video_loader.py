
from youtube_downloader import download_youtube_audio,transcribe_audio
from pathlib import Path
import os

class VideoLoader:
    """
    VideoLoader: Downloads and transcribe Youbute videos into text with caching.\n
    
    This class provides a simple interface to:\n
        1. Chech if the video has already been processed.
        2. Downloads audio from a video using 'download_youtube_audio'.
        3. Transcribe audio to text using 'transcribe_audio'.
        4. Save transcripts in a local cache folder to avoid re-processing.
        5. Clean up temporary audio files automatically.
        
    Usage Exemples:
        loader=VideoLoader(output_dir="video_cache")
        text=loader.process_video("https://www.youtube.com/watch?v=ABC123") \n
        print(text)
        
    Attributes:
        output_dir (Path): Directory where transcripts are stored
    """
    def __init__(self,output_dir="video_cache"):
        self.output_dir=Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def _video_already_processed(self,video_id:str):
        """
        Checks if a transcripts already exists for a given video
        
        Args:
            video_id (str): Youtube video ID
            
        Returns:
            tuple: (exists: bool, txt_path: Path)
                    exists is True if transcript already exists.
                    txt_path is the path to the transcript file.
        """
        txt_path=self.output_dir / f"{video_id}.txt"
        return txt_path.exists(),txt_path
        
    def download_audio(self,url:str):
        """
        Dowloading audio from an Youtube URL.
        
        Args:
            url (str): Youtube video URL.
           
        Returns:
           str: Path to downloaded audio file 
        """
        return download_youtube_audio(url)

    def transcribe(self,audio_path):
        """
        Transcribing audio to text.
        
        Args:
            audio_path (str): Path to audio file.
           
        Returns:
           str: Transcribed text.
        """
        return transcribe_audio(audio_path)
        
    def process_video(self,url)->dict[str,str]:
        """
        Process a video by downloading its audio, transcribing it, and saving the transcript.
        
        Args:
            url (str): Youtube video URL.
           
        Returns:
           str: Transcribed text.
        """
        video_id=url.split("v=")[-1]
        exists,txt_path=self._video_already_processed(video_id)
        metadata = {
            "video_id": video_id,
            "url": url
        }
        if exists:
            with open(txt_path,"r") as f:
                txt= f.read()
                return {
                    "text": txt,
                    "metadatas": metadata
                }

        audio_path=self.download_audio(url)
        text=self.transcribe(audio_path)
        txt_path=self.output_dir / f"{video_id}.txt"
        with open(txt_path,"w",encoding="utf-8") as f:
            f.write(text)
            
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return {
            "text":text,
            "metadata":metadata
        }
