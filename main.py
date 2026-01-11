import config
from src.loader import load_documents
import src.splitter as splitter
from src.vectorstore import create_embeddings, create_vectorstore
from src.llm import create_llm
from src.retriever import create_retriever
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import sys

def main():
    print("--- RAG Pipeline Initializing ---")
    
    # Load and process documents
    documents = load_documents()
    if not documents:
        print("Warning: No documents found. Checking for existing vectorstore...")
        docs = []
    else:
        docs = splitter.split_documents(documents)
        print(f"Documents split into {len(docs)} chunks.")

    # Create embeddings and vectorstore
    try:
        embeddings = create_embeddings()
        vectorstore = create_vectorstore(docs, embeddings)
    except Exception as e:
        print(f"Error during vectorstore initialization: {e}")
        sys.exit(1)

    # Create LLM
    llm = create_llm()

    # Create retriever
    retriever = create_retriever(vectorstore)

    # Define prompt
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are a retrieval-based assistant.
Answer the user's question ONLY using the given CONTEXT.
Do NOT use external knowledge.
Do NOT make assumptions or hallucinate.

Rules:
- Write the answer in TURKISH but using ONLY ASCII characters.
- Do NOT use Turkish characters like: ç, ğ, ş, ı, İ, ö, ü.
- The answer must be SHORT, CLEAR, and DIRECT.
- If the answer is not found in the context, respond exactly with:
  "Baglamda cevap bulunamadi."

CONTEXT:
{context}

QUESTION:
{question}

ASCII TURKISH ANSWER:
"""
    )

    # Create chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt}
    )

    print("\n--- RAG Ready ---")
    print("(Type 'exit' to quit)")
    
    while True:
        try:
            query = input("\nKullanici: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "cikis"]:
                break

            response = chain.invoke({"query": query})
            
            result = ""
            if isinstance(response, dict):
                result = response.get('result', str(response))
            else:
                result = str(response)
                
            print(f"Cevap: {result}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Query error: {e}")

if __name__ == "__main__":
    main()
