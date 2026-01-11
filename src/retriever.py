import config

def create_retriever(vectorstore, search_type="similarity", k=config.SEARCH_K):
    search_kwargs = {"k": k}
    retriever = vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs=search_kwargs
    )
    return retriever
