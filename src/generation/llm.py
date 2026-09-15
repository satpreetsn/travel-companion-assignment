from langchain_ollama import ChatOllama


MODEL_NAME = "gemma3:4b"


def get_llm() -> ChatOllama:
    """
    Return the local Ollama LLM used by PLAN RAG Travel Companion.
    """

    return ChatOllama(
        model=MODEL_NAME,
        temperature=0.8,
    )