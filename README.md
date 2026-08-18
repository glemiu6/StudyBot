# 🤖 Bot-RAG: A Multimodal Retrieval-Augmented Generation Assistant

Bot-RAG is a command-line Retrieval-Augmented Generation (RAG) assistant that lets you **chat with your documents and YouTube videos**. Built on top of the [`pyragcore`](https://pypi.org/project/pyragcore/) library, it ingests local files (PDF, DOCX, Markdown, CSV, TXT) or YouTube videos (transcribed via Whisper), chunks and embeds them, and answers your questions using a configurable LLM — with optional **voice** mode (speech-to-text input + text-to-speech output).

---

## ✨ Features

- 📄 **Multi-format document ingestion** — PDF, DOCX, Markdown, CSV, TXT
- 🎥 **YouTube video support** — downloads audio via `yt-dlp`, transcribes with OpenAI Whisper, and caches transcripts to avoid re-processing
- 🧠 **Pluggable embedding backends** — use a local [Ollama](https://ollama.com) model or HuggingFace `sentence-transformers`
- 💬 **Streaming responses** — answers stream in real time
- 🎙️ **Voice mode** — ask questions by speaking, hear answers read aloud
- 🧩 **Smart chunking** — configurable chunk size, overlap, and top-k retrieval
- 💾 **Chat history export** — save conversations as Markdown files
- ⚡ **Batched embedding** — embeddings computed in batches of 64 with a `tqdm` progress bar
- 🚫 **Deduplication** — already-ingested files/videos are skipped automatically

---

## 📁 Project Structure

```
.
├── main.py                 # Entry point — CLI app, mode selection, chat loop
├── my_config.py            # RagConfig instance (embedding backend, chunking, etc.)
├── rag_pipeline.py         # RagPipeline — extends pyragcore's BasePipeline
├── youtube_downloader.py   # YouTube audio download + Whisper transcription
├── ingest/
│   ├── file_loader.py      # FileLoader — reads PDF/DOCX/MD/CSV/TXT
│   ├── video_loader.py     # VideoLoader — YouTube → transcript with caching
│   └── file_chooser.py     # Interactive file picker
├── utils_io/
│   └── save.py             # Saver — exports chat history to Markdown
└── files/                  # Default folder for documents you want to ingest
```

---

## 🔧 Installation

### 1. Clone the repository
```bash
git clone https://github.com/glemiu6/pyragcore.git
cd bot-rag
```

### 2. Install Python dependencies
```bash
pip install pyragcore[all] yt-dlp openai-whisper pymupdf python-docx pandas tqdm
# Optional, for the sentence-transformers backend:
pip install torch sentence-transformers
```

> **System requirements:**
> - [FFmpeg](https://ffmpeg.org/) — required by `yt-dlp` for audio extraction and by Whisper
> - [Ollama](https://ollama.com) — only if you use the Ollama embedding backend

### 3. (Optional) Pull the Ollama embedding model
```bash
ollama pull mxbai-embed-large
```

---

## ⚙️ Configuration

All runtime settings live in [`my_config.py`](my_config.py). The most important ones:

| Option | Description | Default |
|---|---|---|
| `embedding_backend` | `"ollama"` or `"sentence_transformers"` | `"ollama"` |
| `embedding_model` | Must match the backend | `"mxbai-embed-large:latest"` |
| `device` | `"cuda"` if available, else `"cpu"` | auto-detected |
| `metric` | Similarity metric for retrieval | `"cosine"` |
| `top_k` | Number of chunks retrieved per query | `6` |
| `chunk_size` | Characters per chunk | `600` |
| `chunk_overlap` | Overlap between chunks | `150` |
| `stream` | Stream LLM responses | `True` |
| `voice_enabled` | Enable microphone + TTS | `False` |
| `model_name` | LLM name; `None` triggers interactive `choose_model()` prompt | `None` |

To switch to the **sentence-transformers** backend, comment out Option A and uncomment Option B in `my_config.py`.

---

## 🚀 Usage

### Basic invocation
```bash
python3 main.py <persist_dir> <output_folder>
```
- `persist_dir` — where the vector store is persisted (e.g. `./vectordb`)
- `output_folder` — where chat exports are saved (e.g. `./output`)

### Example session
```bash
python3 main.py ./vectordb ./output
```

You'll be prompted to choose:

1. **Source mode**
   - `1` — Process a file (picks from `./files/`)
   - `2` — Process a YouTube video (paste URL)

2. **Interaction mode**
   - `1` — Write questions (type `exit`, `quit`, or `q` to stop)
   - `2` — Speak questions (voice input + spoken answers)

3. **Save** — optionally export the conversation as a Markdown file.

### Standalone scripts

**Ingest a single file and ask one question:**
```bash
python3 rag_pipeline.py ./vectordb ./output
```

**Test YouTube transcription:**
```bash
python3 youtube_downloader.py
```

---

## 🧠 How It Works

```
                ┌──────────────────┐
   File/Video ─▶│  Loader          │─▶ text + metadata
                └────────┬─────────┘
                         ▼
                ┌──────────────────┐
                │  Chunker         │─▶ chunks (size=600, overlap=150)
                └────────┬─────────┘
                         ▼
                ┌──────────────────┐
                │  Embedder        │─▶ vectors (batch size 64)
                │  (Ollama / ST)   │
                └────────┬─────────┘
                         ▼
                ┌──────────────────┐
                │  Vector Store    │◀── persisted in <persist_dir>
                └────────┬─────────┘
                         ▼
   User query ──▶ Retrieve top-k ──▶ LLM (streamed) ──▶ Answer
```

- **FileLoader** hashes the file name to produce a stable `file_id`, so re-ingesting the same file is skipped.
- **VideoLoader** caches transcripts as `<video_id>.txt` in `./video_cache/`, so subsequent runs are instant.
- **RagPipeline** inherits chunking, embedding, retrieval, and LLM calls from `pyragcore.BasePipeline`.

---

## 📄 Supported File Formats

| Format | Library Used |
|---|---|
| `.pdf`  | PyMuPDF (`fitz`) |
| `.docx` | `python-docx` |
| `.md`   | built-in `open()` |
| `.txt`  | built-in `open()` |
| `.csv`  | `pandas` (each row becomes a `key:value` string) |

Other extensions raise `FileNotSupportedException`.

---

## 💾 Chat Export

When you choose to save, the conversation is written to `<output_folder>/<name>.md` (or auto-named `chat_<id>_<timestamp>.md`) in Markdown format:

```markdown
## User: What is this file about?

## Assistant:
<response>
```

---

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| `torch` import error | Only needed for the `sentence_transformers` backend; the app falls back to CPU automatically |
| YouTube download fails | Ensure `ffmpeg` is installed and the URL is valid |
| Whisper is slow | Use a smaller model (`"tiny"` / `"base"`) in `youtube_downloader.py` |
| CUDA not detected | Verify your PyTorch install matches your CUDA version |
| `FileNotSupportedException` | Add the file to `FileLoader.reader` or convert to a supported format |

---

## 📦 Dependencies

- [`pyragcore`](https://pypi.org/project/pyragcore/) — core RAG framework
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) — YouTube audio download
- [`openai-whisper`](https://github.com/openai/whisper) — audio transcription
- [`pymupdf`](https://pymupdf.readthedocs.io/) — PDF reading
- [`python-docx`](https://python-docx.readthedocs.io/) — DOCX reading
- [`pandas`](https://pandas.pydata.org/) — CSV reading
- [`tqdm`](https://github.com/tqdm/tqdm) — progress bars
- [`torch`](https://pytorch.org/) + [`sentence-transformers`](https://www.sbert.net/) — optional embedding backend
- [Ollama](https://ollama.com) — optional local embedding backend

---

## 📜 License

This project is provided as-is for educational and personal use. Please check the licenses of each dependency before redistribution.

---

## 🙌 Acknowledgements

Built on the [`pyragcore`](https://pypi.org/project/pyragcore/) framework. Thanks to the open-source communities behind Whisper, yt-dlp, PyMuPDF, and sentence-transformers.