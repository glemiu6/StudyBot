import sys
from tqdm import tqdm
from ingest.file_loader import FileLoader
from ingest.video_loader import VideoLoader
from pyragcore import BasePipeline
from utils_io.save import Saver
from pyragcore.ingestion.chunker import Chunker
from pyragcore.utils_io.logger import get_logger
logger=get_logger(__name__)

from utils_io.file_chooser import choose_file

class RagPipeline(BasePipeline):
    def __init__(self,persist_dir:str,output_folder:str):
        super().__init__(persist_dir,output_folder)
        print(f"Using model: {self.model_name}\n\n")
        self.chunker=Chunker()




    def ingest(self, folder: str):
        loader = FileLoader()

        file = choose_file(folder)
        if file is None:
            print("No files found.")
            return None
        content = loader.read(file)
        text = content.get("text", '')
        metadata = content.get("metadatas", {})
        file_id = metadata.get("file_id", '')
        if self._is_ingested(file_id):
            print(f"File already ingested, skipping...")
            return file_id
        chunks = self.chunker.chunk(text, metadata)

        documents, metadatas, ids = [], [], []


        for i, item in enumerate(chunks):
            documents.append(item["chunk"])
            metadatas.append(item["metadatas"])
            ids.append(f"{file_id}_chunk_{i}")

        logger.info(f"Chunked into {len(documents)} chunks, embedding...")

        BATCH_SIZE = 64
        all_embeddings = []
        for start in tqdm(range(0, len(documents), BATCH_SIZE), desc="Embedding"):
            batch = documents[start:start + BATCH_SIZE]
            all_embeddings.extend(self.embedder.embed(batch))

        self.vector_store.add(
            embeddings=all_embeddings,
            documents=documents,
            metadata=metadatas,
            ids=ids
        )
        return file_id




    def ingest_video(self,url:str) :
        loader=VideoLoader()

        content=loader.process_video(url)
        text=content.get("text",'')
        metadata=content.get("metadata",{})
        BATCH_SIZE = 64
        chunks=self.chunker.chunk(text,metadata)
        document,metadatas,ids=[],[],[]
        video_id=metadata.get("video_id",'')

        for i,item in enumerate(chunks):
            document.append(item["chunk"])
            metadatas.append(item["metadatas"])
            ids.append(f"{video_id}_chunk_{i}")


        for start in range(0,len(document),BATCH_SIZE):
            end=start+BATCH_SIZE
            batch_docs=document[start:end]
            batch_meta=metadatas[start:end]
            batch_ids=ids[start:end]

            batch_embeddings=self.embedder.embed(batch_docs)
            self.vector_store.add(embeddings=batch_embeddings,documents=batch_docs,metadata=batch_meta,ids=batch_ids)
        return video_id

    def save(self, text: list[dict[str, str]]):
        saver = Saver(self.output_folder)
        name = input("Enter a name (or press Enter for auto-name): ").strip()
        saver.save_chat(text, name if name else None)

if __name__=="__main__":
    rag=RagPipeline(persist_dir=sys.argv[1],output_folder=sys.argv[2])
    file=rag.ingest("./files")
    ans= rag.ask("What is this file about?",file)
    print(ans)



