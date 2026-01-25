import re           # regex based text cleaning
import docx         # reads docx files
import pymupdf      # reads pdf files
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import pipeline   # huggingface api for ml model inference


class DocumentSummarizer:
    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn", # bart-large-cnn: standard model for summarization, fine-tuned on CNN Daily mail
        chunk_size: int = 225,
        chunk_overlap: int = 60
    ):
        self.summarizer = pipeline("summarization", model_name = model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,                    # chunk size (characters)
            chunk_overlap = chunk_overlap,              # character overlap when chunking (preventing )
            separators = ["\n\n", ". ", "? ", "! "],    # splits on: paragraphs and sentences (., ?, !)
            keep_separator = True                       # keeps punctuation
        )

    def split_text(self, text: str) -> list[str]:
        if not text.strip():
            return []

        # clean text w/ re by converting all white space into single spaces
        text = re.sub(r'\s+', ' ', text).strip()

        chunks = self.text_splitter.split_text(text)
        return chunks

    def summarize_chunk(self, chunk: str) -> str:
        result = self.summarizer(
            chunk,
            min_length = 80,
            max_length = 300,
            do_sample = False,  # greedy decoding (deterministic)
            truncation = True
        )
        return result[0]["summary_text"] if result else ""

    # Hierarchy: Summarize each chunks, then summarize their summaries
    def summarize_document(self, text: str) -> str:
        chunks = self.split_text(text)
        if not chunks:
            return ""

        chunk_summaries = [
            self.summarize_chunk(chunk) for chunk in chunks
        ]

        combined_summaries = " ".join(chunk_summaries)

        final_summary = self.summarizer(
            combined_summaries,
            min_length = 120,
            max_length = 350,
            do_sample = False,
            truncation = True
        )
        
        return final_summary[0]["summary_text"] if final_summary else ""


def extract_text_from_pdf(file_path: str | Path) -> str:
    try:
        doc = pymupdf.open(file_path)
        text = "\n".join(page.get_text("text") for page in doc)
        doc.close()
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")

def extract_text_from_docx(file_path: str | Path) -> str:
    try:
        doc = docx.Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
    except Exception as e:
        raise ValueError(f"Error extracting text from DOCX: {str(e)}")

def extract_text_from_txt(file_path: str | Path) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read().strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from TXT: {str(e)}")

def extract_text_from_file(file_path: str | Path, file_type: str) -> str:
    """Extract text from file based on file type"""
    file_type = file_type.lower()
    
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type == "docx":
        return extract_text_from_docx(file_path)
    elif file_type == "txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
