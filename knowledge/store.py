from langchain_community.vectorstores import FAISS
from knowledge.sample_data import SAMPLE_DOCUMENTS
from utils.llm import get_embeddings


_store: FAISS | None = None


def get_store() -> FAISS:
    global _store
    if _store is None:
        embeddings = get_embeddings()
        texts = [doc["text"] for doc in SAMPLE_DOCUMENTS]
        metadatas = [{"source": doc["source"]} for doc in SAMPLE_DOCUMENTS]
        _store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
    return _store


def search(query: str, k: int = 3) -> list[str]:
    store = get_store()
    docs = store.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]
