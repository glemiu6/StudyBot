import hashlib
from pyragcore.ingestion.base_loader import BaseLoader
from pyragcore.exceptions import FileNotSupportedException
import fitz
import pandas as pd
from docx import Document
from pathlib import Path




class FileLoader(BaseLoader):
    """
    FileLoader: Reads multiple types of file. \n

    The class provides a simple interface to:\n
        1. Reads files using the `read` function.

    Types of files that supports:\n
        - PDF
        - DOCX
        - MD
        - CSV
        - TXT

    Usage Examples:

        loader = FileLoader()
        text = loader.read(folder/file.txt)
        print(text["text"])
    """


    def read(self,path)-> dict[str, str | dict[str, str | int | float]]:
        """
        Reads the files using helper functions.

        Args:
            path(str): The path to the file

        Returns:
            dict: The file content and metadata
        """
        p = Path(path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        reader={
            ".pdf":self.read_pdf,
            ".docx":self.read_docx,
            ".md":self.read_md,
            ".csv":self.read_csv,
            ".txt":self.read_md
        }
        ext=p.suffix
        if ext not in reader.keys():
            raise FileNotSupportedException(f"File format not supported: {ext}")
        text= reader[ext](path)
        metadata={
            "file_id":hashlib.sha256(str(p.name).encode("utf-8")).hexdigest(),
            "file_type":ext,
            "file_size":p.stat().st_size,
            "file_name":p.name,
            "source":str(p),
            "modified":p.stat().st_mtime
        }
        return {
            "text":text,
            "metadatas":metadata
        }






    @staticmethod
    def read_pdf(path):
        """
        Function that read PDF files. \n

        Mostly used as a helper function.\n

        Uses the `fitz` library to read the file.

        Args:
            path: The path to the file

        Returns:
            str: File contents
        """
        text = ''
        document = fitz.open(path)
        for page in document:
            text += page.get_text() + '\n'
        return text


    @staticmethod
    def read_docx(path):
        text = ''
        document = Document(path)
        for page in document.paragraphs:
            text += page.text + '\n'
        return text

    @staticmethod
    def read_csv(path):
        df = pd.read_csv(path)
        data = df.to_dict(orient="records")
        all_rows = []
        for d in data:
            text_rows = ','.join(f"{key}:{value}" for key, value in d.items())
            all_rows.append(text_rows)
        return "\n".join(all_rows)


    @staticmethod
    def read_md(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()



