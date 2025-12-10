from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama
from dotenv import load_dotenv
import glob, os

load_dotenv()

pdf_folder = "data"
pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"))
pdf_files = pdf_files[:5]

print(f"Loaded PDF files: {pdf_files}")

documents = []
for pdf_path in pdf_files:
    loader = PyPDFLoader(pdf_path)
    documents.extend(loader.load())

print(f"Total pages: {len(documents)}")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120
)
docs = text_splitter.split_documents(documents)
print(f"Total chunks: {len(docs)}")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "my_documents"

if os.path.exists(CHROMA_PATH):
    print("Loading existing database...")
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )
else:
    print("Creating new database...")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION_NAME,
    )
    print("Database created!")

llm = Ollama(
    model="llama3:8b",
    temperature=0
)

retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 6,
        "score_threshold": 0.2
    }
)


def format_docs(docs):
    if not docs:
        return ""
    return "\n\n".join(doc.page_content for doc in docs)

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a RAG assistant. Answer ONLY using the given CONTEXT.

CRITICAL RULES:
1. Use ONLY information from CONTEXT
2. Do NOT add external knowledge
3. Do NOT guess or hallucinate
4. If CONTEXT is empty or IRRELEVANT to the question, respond exactly with:
   "Answer not found in context."
5. Write the answer in Turkish using ASCII characters (c, g, s, i, o, u)
6. Answer should be 3-6 sentences long

CONTEXT:
{context}

QUESTION: {question}

ANSWER (ONLY from CONTEXT):"""
)

print("\n---RAG System Ready---")
print("Type 'exit' to quit\n")

while True:
    query = input("User: ")
    if query.lower() == "exit":
        break

    try:
        # Tek seferde retrieval + LLM (daha verimli)
        retrieved_docs = retriever.invoke(query)
        print(f"\n[DEBUG] {len(retrieved_docs)} relevant documents found")
        
        if not retrieved_docs:
            print("\nAnswer: Answer not found in context.\n")
            continue
        
        # Manuel olarak context oluştur ve LLM'e gönder (çift retrieval'dan kaçın)
        context = format_docs(retrieved_docs)
        formatted_prompt = prompt.format(context=context, question=query)
        response = llm.invoke(formatted_prompt)
        print(f"\nAnswer: {response}\n")
    except Exception as e:
        print(f"Error: {e}")
