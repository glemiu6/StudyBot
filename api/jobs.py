import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable,Any

TTL_SECONDS = 3600

@dataclass
class Job:
    id:str
    kind:str
    status:str = "queued" # queued -> running -> done | error
    result:Any = None
    error:str|None = None
    created_at:float = field(default_factory=time.time)

class JobManager:
    """
    Tracks background ingestion jobs. Ingestion (file parsing, chunking,
    embedding, Whisper transcription) is slow and blocking — it must never
    run directly inside an HTTP request handler, or it stalls every other
    request on the server. Each job instead runs in its own daemon thread;
    the client polls GET /api/jobs/{id} for status.

    Finished jobs (done/error) older than ttl_seconds are swept on the next
    create() call, so a long-running server doesn't accumulate job records
    forever.
    """

    def __init__(self, ttl_seconds:int=TTL_SECONDS):
        self._jobs:dict[str,Job] = {}
        self._lock = threading.Lock()
        self._ttl = ttl_seconds

    def create(self,kind:str)->Job:
        job = Job(id=str(uuid.uuid4().hex),kind=kind)
        with self._lock:
            self._jobs[job.id]=job
            self._sweep_locked()
        return job

    def get(self,job_id:str)->Job|None:
        with self._lock:
            return self._jobs.get(job_id)


    def run(self,job:Job,func:Callable,*args,**kwargs):
        def _target():
            job.status="running"
            try:
                job.result=func(*args,**kwargs)
                job.status="done"
            except Exception as e:
                job.error=str(e)
                job.status="error"
        threading.Thread(target=_target,daemon=True).start()


    def _sweep_locked(self):
        cutoff = time.time() - self._ttl
        stale =[
            jid for jid,j in self._jobs.items() if j.status in ("done","error") and j.created_at < cutoff
        ]
        for jid in stale:
            del self._jobs[jid]