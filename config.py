import os
from dotenv import load_dotenv

load_dotenv()

# Project Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

# Model Configurations
LLM_MODEL = "llama3:8b"
EMBEDDING_MODEL = "BAAI/bge-m3"
DEVICE = "cpu"

# PDF path
PDF_PATH = os.path.join(DATA_DIR, "yzetik.pdf")

# Splitter Configuration
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

# Retriever Configuration
SEARCH_K = 5
