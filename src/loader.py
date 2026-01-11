from langchain_community.document_loaders import PyPDFLoader
import os
import config

def load_documents(pdf_path=config.PDF_PATH):
    if not os.path.exists(pdf_path):
        print(f"Warning: PDF file not found at {pdf_path}")
        return []
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        return documents
    except Exception as e:
        print(f"PDF load error: {e}")
        return []
