from fastapi import FastAPI, Request
from pydantic import BaseModel
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import time
from datetime import datetime
from contextlib import asynccontextmanager

# ─────────────────────────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('rag_api.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# METRICS TRACKING
# ─────────────────────────────────────────────────────────────
class Metrics:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_retrieval_time = 0.0
        self.total_llm_time = 0.0
        self.total_response_time = 0.0
        self.start_time = datetime.now()
    
    def record_request(self, success: bool, retrieval_time: float, llm_time: float, total_time: float):
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.total_retrieval_time += retrieval_time
        self.total_llm_time += llm_time
        self.total_response_time += total_time
    
    def get_stats(self):
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": round(self.successful_requests / self.total_requests * 100, 2) if self.total_requests > 0 else 0,
            "avg_retrieval_time": round(self.total_retrieval_time / self.total_requests, 3) if self.total_requests > 0 else 0,
            "avg_llm_time": round(self.total_llm_time / self.total_requests, 3) if self.total_requests > 0 else 0,
            "avg_response_time": round(self.total_response_time / self.total_requests, 3) if self.total_requests > 0 else 0,
            "requests_per_second": round(self.total_requests / uptime, 2) if uptime > 0 else 0,
            "uptime_seconds": round(uptime, 2)
        }

metrics = Metrics()

# ─────────────────────────────────────────────────────────────
# LIFESPAN (Startup/Shutdown)
# ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting RAG API Server...")
    logger.info("Model: Qwen/Qwen2.5-3B-Instruct")
    logger.info("Vector DB: ChromaDB")
    logger.info("vLLM Endpoint: http://localhost:8080/v1")
    yield
    logger.info("Shutting down RAG API Server...")

app = FastAPI(
    title="RAG API with vLLM",
    description="Production-ready RAG API with detailed logging and metrics",
    version="2.0.0",
    lifespan=lifespan
)

executor = ThreadPoolExecutor(max_workers=50)

# ─────────────────────────────────────────────────────────────
# EMBEDDINGS & VECTORSTORE
# ─────────────────────────────────────────────────────────────
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "my_documents"

vectorstore = Chroma(
    persist_directory=CHROMA_PATH,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
)

# ─────────────────────────────────────────────────────────────
# LLM CONFIGURATION
# ─────────────────────────────────────────────────────────────
llm = ChatOpenAI(
    model="Qwen/Qwen2.5-3B-Instruct",
    openai_api_key="EMPTY",
    openai_api_base="http://localhost:8080/v1",
    temperature=0.3,
    max_tokens=512,
)

retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 6,
        "score_threshold": 0.2
    }
)

# ─────────────────────────────────────────────────────────────
# PROMPT TEMPLATE
# ─────────────────────────────────────────────────────────────
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a RAG assistant. Answer ONLY using the given CONTEXT.

CRITICAL RULES:
1. Use ONLY information from CONTEXT
2. Do NOT add external knowledge
3. Do NOT guess or hallucinate
4. If CONTEXT is empty or IRRELEVANT to the question, respond exactly with:
   "Answer not found in context."
5. Write the answer in Turkish using ASCII characters

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
)

def format_docs(docs):
    if not docs:
        return ""
    return "\n\n".join(doc.page_content for doc in docs)

# ─────────────────────────────────────────────────────────────
# QUERY PROCESSING
# ─────────────────────────────────────────────────────────────
class Query(BaseModel):
    question: str

def process_query_sync(question: str) -> tuple[str, float, float, float]:
    """
    Synchronous query processing - retrieval and LLM in one call
    Returns: (answer, retrieval_time, llm_time, total_time)
    """
    start_total = time.time()
    
    # 1. Retrieval
    start_retrieval = time.time()
    retrieved_docs = retriever.invoke(question)
    retrieval_time = time.time() - start_retrieval
    
    if not retrieved_docs:
        total_time = time.time() - start_total
        logger.warning(f"No docs found | Q: {question[:50]}... | Retrieval: {retrieval_time:.3f}s")
        return "Answer not found in context.", retrieval_time, 0.0, total_time
    
    # 2. LLM Generation
    start_llm = time.time()
    context = format_docs(retrieved_docs)
    formatted_prompt = prompt.format(context=context, question=question)
    response = llm.invoke(formatted_prompt)
    llm_time = time.time() - start_llm
    
    total_time = time.time() - start_total
    
    logger.info(
        f"Query OK | "
        f"Docs: {len(retrieved_docs)} | "
        f"Retrieval: {retrieval_time:.3f}s | "
        f"LLM: {llm_time:.3f}s | "
        f"Total: {total_time:.3f}s | "
        f"Q: {question[:40]}..."
    )
    
    return response.content, retrieval_time, llm_time, total_time

# ─────────────────────────────────────────────────────────────
# API ENDPOINTS
# ─────────────────────────────────────────────────────────────
@app.post("/query")
async def query(q: Query):
    loop = asyncio.get_event_loop()
    try:
        answer, retrieval_time, llm_time, total_time = await loop.run_in_executor(
            executor, process_query_sync, q.question
        )
        metrics.record_request(True, retrieval_time, llm_time, total_time)
        return {
            "answer": answer,
            "metrics": {
                "retrieval_time": round(retrieval_time, 3),
                "llm_time": round(llm_time, 3),
                "total_time": round(total_time, 3)
            }
        }
    except Exception as e:
        logger.error(f"Query failed | Error: {str(e)} | Q: {q.question[:50]}...")
        metrics.record_request(False, 0, 0, 0)
        return {"answer": "An error occurred while processing your query.", "error": str(e)}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.get("/metrics")
def get_metrics():
    """Get detailed performance metrics"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics.get_stats()
    }

@app.get("/stats")
def get_stats():
    """Get vectorstore statistics"""
    try:
        collection = vectorstore._collection
        return {
            "status": "ok",
            "vectorstore": {
                "total_documents": collection.count(),
                "collection_name": COLLECTION_NAME
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
