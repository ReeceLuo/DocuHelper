import re           # regex based text cleaning
import docx         # reads docx files
import pymupdf      # reads pdf files
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import pipeline   # huggingface api for ml model inference


# BART has 1024-token input limit; ~4 chars/token -> ~4000 chars. Stay under for safety.
SINGLE_SUMMARY_MAX_CHAR = 3000


class DocumentSummarizer:
    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn", # bart-large-cnn: standard model for summarization, fine-tuned on CNN Daily mail
        chunk_size: int = 600,   # chars per chunk (fits in one BART call)
        chunk_overlap: int = 60,
        single_summary_max_char: int = SINGLE_SUMMARY_MAX_CHAR,
    ):
        self.summarizer = pipeline("summarization", model_name = model_name)
        self.single_summary_max_char = single_summary_max_char
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,                    # chunk size (characters)
            chunk_overlap = chunk_overlap,              # character overlap when chunking (preventing )
            separators = ["\n\n", ". ", "? ", "! "],    # splits on: paragraphs and sentences (., ?, !)
            keep_separator = True                       # keeps punctuation
        )

    def split_text(self, text: str) -> list[str]:
        if not text.strip():
            return []
      
        chunks = self.text_splitter.split_text(text)
        return chunks

    def summarize_text(self, text: str, min_len: int = 80, max_len: int = 300) -> str:
        result = self.summarizer(
            text,
            min_length=min_len,
            max_length=max_len,
            do_sample=False,
            truncation=True,
        )
        return result[0]["summary_text"] if result else ""

    def summarize_document(self, text: str) -> str:
        """One summary for the whole document. Uses single pass when short, else chunk → summarize each → summarize combined."""
        # Clean text w/ re by converting all white space into single spaces
        cleaned = re.sub(r"\s+", " ", text).strip()
        if not cleaned:
            return ""

        # Short doc: one pass (better coherence, faster)
        if len(cleaned) <= self.max_chars_single:
            return self.summarize_text(cleaned, min_len = 80, max_len = 300)

        # Long doc: chunk → summarize each → summarize the combined summaries
        chunks = self.split_text(text)
        if not chunks:
            return ""

        chunk_summaries = [self.summarize_text(c) for c in chunks]
        combined = " ".join(chunk_summaries)
        final_summary = self.summarize_text(combined, min_len = 120, max_len = 350)
        
        return final_summary[0]["summary_text"] if final_summary else ""

# Global instance
summarizer = DocumentSummarizer()

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
