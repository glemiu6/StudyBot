from pathlib import Path

from fastapi import FastAPI, UploadFile,File,Depends,HTTPException,Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field,HttpUrl

from pyragcore.exceptions import BotRagException
from api.service import RagService

ALLOWED_EXTENSIONS = {".pdf", ".docx",".txt",".csv",".md"}
FILE_SIZE_LIMIT = 50 * 1024 * 1024


app = FastAPI(title="StudyBot",version="0.1.0")

def get_service()->RagService:
    if not hasattr(app.state,"service"):
        app.state.service=RagService()
    return app.state.service

@app.exception_handler(BotRagException)
def handle_bot_rag_exceptions(req:Request,exc:BotRagException):
    return JSONResponse(status_code=502,content={"error":str(exc)})


@app.get("/health")
def health():
    return {"status":"ok"}

class VideoRequest(BaseModel):
    url:HttpUrl

class ChatMessage(BaseModel):
    role:str
    content:str

class ChatRequest(BaseModel):
    question:str = Field(...,min_length=1)
    source_id:str|None = None
    history:list[ChatMessage] = []

@app.post("/api/files")
async def upload_file(file:UploadFile = File(...),service:RagService=Depends(get_service)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed types: {sorted(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")

    if len(content) > FILE_SIZE_LIMIT:
        raise HTTPException(
            status_code=413, detail=f"File size exceeds  {FILE_SIZE_LIMIT // (1024 * 1024)} MB upload limit",
        )

    job = service.start_file_ingestion(file.filename,content)
    return {"job_id":job.id}


@app.post("/api/video")
async def upload_video(req:VideoRequest,service:RagService=Depends(get_service)):
    job = service.start_video_ingestion(str(req.url))
    return {"job_id":job.id}

@app.get("/api/jobs/{job_id}")
def get_job(job_id:str,service:RagService=Depends(get_service)):
    job = service.jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404,detail=f"Job {job_id} not found")
    return {"status":job.status,"result":job.result,"error":job.error}

@app.get("/api/sources")
def list_sources(service:RagService=Depends(get_service)):
    return service.list_sources()


@app.get("/api/models")
def list_models(service:RagService=Depends(get_service)):
    return service.list_models()

@app.post("/api/chat")
def chat(req:ChatRequest,service:RagService=Depends(get_service)):
    history=[{"role":m.role,"message":m.content} for m in req.history]
    answer= service.ask(
        req.question,
        req.source_id,
        history)
    return {"answer":answer}



FRONTEND_DIR=Path(__file__).resolve().parent.parent/"frontend"

if FRONTEND_DIR.exists():
    app.mount("/",StaticFiles(directory=str(FRONTEND_DIR)),name="app")