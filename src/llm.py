from langchain_ollama import OllamaLLM
import config

def create_llm(model=config.LLM_MODEL, temperature=0.3):
    llm = OllamaLLM(
        model=model,
        temperature=temperature
    )
    return llm
