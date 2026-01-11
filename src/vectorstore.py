import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import config

def create_embeddings(model_name=config.EMBEDDING_MODEL, device=config.DEVICE):
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True}
    )
    return embeddings

def create_vectorstore(docs, embeddings, persist_directory=config.CHROMA_DIR):
    if os.path.exists(persist_directory) and len(os.listdir(persist_directory)) > 0:
        print(f"Loading existing vectorstore from {persist_directory}")
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
    else:
        if not docs:
            raise ValueError("No documents provided to create vectorstore and no existing vectorstore found.")
        print(f"Creating new vectorstore in {persist_directory}")
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=persist_directory
        )
    return vectorstore
