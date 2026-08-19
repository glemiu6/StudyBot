import os
from pyragcore import RagConfig

try:
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError:
    # torch is only needed for the sentence_transformers backend — don't crash if it's missing
    device = "cpu"

my_config = RagConfig(
    device=device,

    embedding_backend="ollama",
    embedding_model="mxbai-embed-large:latest",

   
    ollama_base_url=os.environ.get("OLLAMA_BASE_URL","http://localhost:11434"),

    model_name=os.environ.get("MODEL_NAME", "granite3-dense:8b"),
    metric="cosine",
    top_k=6,
    chunk_size=600,
    chunk_overlap=150,
    stream=True,
    voice_enabled=False,
)