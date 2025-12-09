# api_server.py - RAG API Server with Ollama
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.llms import Ollama
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI(title="RAG API")

# Thread pool
executor = ThreadPoolExecutor(max_workers=20)

# Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# Vector store
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

# LLM - Ollama
llm = Ollama(model="llama3:8b", temperature=0.3)

# Retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

# Prompt
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
Context: {context}
Question: {question}
Answer in Turkish (ASCII only):"""
)

# RAG Chain
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

class Query(BaseModel):
    question: str

@app.post("/query")
async def query(q: Query):
    loop = asyncio.get_event_loop()
    answer = await loop.run_in_executor(executor, rag_chain.invoke, q.question)
    return {"answer": answer}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
