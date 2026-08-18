from pyragcore import RagConfig

try:
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError:
    # torch is only needed for the sentence_transformers backend — don't crash if it's missing
    device = "cpu"

my_config = RagConfig(
    device=device,

    # --- embedding backend + model MUST match each other ---
    # Option A (local, no HF download, needs `ollama pull mxbai-embed-large`):
    embedding_backend="ollama",
    embedding_model="mxbai-embed-large:latest",

    # Option B (sentence-transformers, downloads from HF hub, uses `device` above):
    # embedding_backend="sentence_transformers",
    # embedding_model="all-mpnet-base-v2",

    model_name=None,       # set explicitly to skip the interactive choose_model() prompt
    metric="cosine",
    top_k=6,                     # a bit more context for study Q&A
    chunk_size=600,
    chunk_overlap=150,
    stream=True,
    voice_enabled=False,         # flip True once you're testing voice mode
)