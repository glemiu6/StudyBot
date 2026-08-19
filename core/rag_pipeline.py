import sys
from tqdm import tqdm

from core.ingest.file_loader import FileLoader
from core.ingest.video_loader import VideoLoader
from core.utils_io.save import Saver
from core.utils_io.file_chooser import choose_file

from pyragcore.pipeline.base_pipeline import BasePipeline
from pyragcore.utils_io.logger import get_logger
from my_config import my_config

logger = get_logger(__name__)


class RagPipeline(BasePipeline):
    def __init__(self, persist_dir: str, output_folder: str):
        super().__init__(persist_dir, output_folder, config=my_config)
        print(f"Using model: {self.model_name}\n\n")
        # self.chunker is already set by BasePipeline.__init__ — no need to re-create it here

    def ingest(self, folder: str):
        loader = FileLoader()

        file = choose_file(folder)
        if file is None:
            print("No files found.")
            return None

        content = loader.read(file)
        text = content.get("text", "")
        metadata = content.get("metadatas", {})
        file_id = metadata.get("file_id", "")

        if self._is_ingested(file_id):
            print("File already ingested, skipping...")
            return file_id

        chunks = self.chunk_text(text, metadata)  # respects RagConfig chunk_size/overlap/max_tokens
        documents = [c["chunk"] for c in chunks]
        metadatas = [c["metadatas"] for c in chunks]
        ids = [f"{file_id}_chunk_{i}" for i in range(len(chunks))]

        logger.info(f"Chunked into {len(documents)} chunks, embedding...")

        BATCH_SIZE = 64
        all_embeddings = []
        for start in tqdm(range(0, len(documents), BATCH_SIZE), desc="Embedding"):
            batch = documents[start:start + BATCH_SIZE]
            all_embeddings.extend(self.embedder.embed(batch))

        self.add_to_store(all_embeddings, documents, metadatas, ids)  # tags vectors with embedder
        return file_id

    def ingest_video(self, url: str):
        from youtube_downloader import extract_video_id
        video_id = extract_video_id(url)

        if self._is_ingested(video_id):
            print("Video already ingested, skipping...")
            return video_id

        loader = VideoLoader()
        content = loader.process_video(url)
        text = content.get("text", "")
        metadata = content.get("metadatas", {})  # VideoLoader now returns "metadatas", matching FileLoader

        chunks = self.chunk_text(text, metadata)
        documents = [c["chunk"] for c in chunks]
        metadatas = [c["metadatas"] for c in chunks]
        ids = [f"{video_id}_chunk_{i}" for i in range(len(chunks))]

        logger.info(f"Chunked video into {len(documents)} chunks, embedding...")

        BATCH_SIZE = 64
        for start in tqdm(range(0, len(documents), BATCH_SIZE), desc="Embedding video"):
            end = start + BATCH_SIZE
            batch_docs = documents[start:end]
            batch_meta = metadatas[start:end]
            batch_ids = ids[start:end]
            batch_embeddings = self.embedder.embed(batch_docs)
            self.add_to_store(batch_embeddings, batch_docs, batch_meta, batch_ids)

        return video_id

    def save(self, text: list[dict[str, str]]):
        saver = Saver(self.output_folder)
        name = input("Enter a name (or press Enter for auto-name): ").strip()
        saver.save_chat(text, name if name else None)


if __name__ == "__main__":
    rag = RagPipeline(persist_dir=sys.argv[1], output_folder=sys.argv[2])
    file_id = rag.ingest("./files")
    ans = rag.ask("What is this file about?", file_id)
    print(ans)