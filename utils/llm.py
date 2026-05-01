from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from config import GOOGLE_API_KEY, LLM_MODEL, WEAK_LLM_MODEL, EMBEDDING_MODEL


def get_llm(
    temperature: float = 0.5,
    max_tokens: int = 1024,
    weak: bool = False,
) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=WEAK_LLM_MODEL if weak else LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=temperature,
        max_output_tokens=max_tokens,
    )


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
    )
