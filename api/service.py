import os
import uuid

from core.rag_pipeline import RagPipeline
from pyragcore.utils_io.logger import get_logger
from api.jobs import JobManager,Job

logger = get_logger(__name__)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/studybot_uploads")
PERSIST_DIR = os.environ.get("PERSIST_DIR", "/data/persist")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/data/output")


os.makedirs(UPLOAD_DIR, exist_ok=True)

class RagService:
    def __init__(self):
        self.pipeline = RagPipeline(persist_dir=PERSIST_DIR, output_folder=OUTPUT_DIR)
        self.jobs = JobManager()

    def start_file_ingestion(self,file_name:str,content:bytes) -> Job:
        job = self.jobs.create("file")
        safe_name = os.path.basename(file_name or "upload")
        dest = os.path.join(UPLOAD_DIR,f"{uuid.uuid4().hex}_{safe_name}")
        with open(dest,"wb") as f:
            f.write(content)
        self.jobs.run(job,self._ingest_file_and_cleanup,dest)
        return job

    def _ingest_file_and_cleanup(self,file_path:str):
        try:
            return self.pipeline.ingest(file_path)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def start_video_ingestion(self,url:str) -> Job:
        job = self.jobs.create("video")
        self.jobs.run(job,self.pipeline.ingest_video,url)
        return job

    def list_sources(self)->list[dict]:
        return self.pipeline.get_ingested_sources()

    def ask(self,question:str,source_id:str|None,history:list[dict]|None):
        return self.pipeline.ask(question,source_id,history,stream=False)

    def list_models(self)->list[str]:
        try:
            import ollama

            client = ollama.Client(host=self.pipeline.config.ollama_base_url)
            data= client.list()
            return [m.get("model","") for m in data.get("models",[])]
        except Exception as e:
            logger.warning(f"Could not list models: {e}")
            return []

