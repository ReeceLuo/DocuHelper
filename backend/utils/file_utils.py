import re           # regex based text cleaning
import docx         # reads docx files
import pymupdf      # reads pdf files
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import pipeline   # huggingface api for ml model inference

summarizer = pipeline("summarization", model = "facebook/bart-large-cnn")


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
        return self.summarizer(
            chunk,
            min_length = 80,
            max_length = 300,
            do_sample = False,  # greedy decoding (deterministic)
            truncation = True
        )

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

        return final_summary


def extract_text_from_pdf(file_path):
    doc = pymupdf.open(file_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text.strip()

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
