import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

FAST_MODEL = "llama-3.1-8b-instant"
REASONING_MODEL = "llama-3.3-70b-versatile"

try:
    from langchain_groq import ChatGroq
    HAS_LANGCHAIN_GROQ = True
except ImportError:
    HAS_LANGCHAIN_GROQ = False
    ChatGroq = None


def get_llm(
    fast: bool = False,
    temperature: float = 0.2,
    api_key: Optional[str] = None,
    **kwargs
):
    """
    Returns a configured ChatGroq instance.
    """
    if not HAS_LANGCHAIN_GROQ or ChatGroq is None:
        raise ImportError(
            "langchain-groq is not installed. Please run 'pip install -r requirements.txt'."
        )

    groq_api_key = api_key or os.getenv("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        raise ValueError(
            "GROQ_API_KEY is not set or invalid. Please configure your GROQ_API_KEY in the .env file."
        )

    model_name = FAST_MODEL if fast else REASONING_MODEL

    return ChatGroq(
        model_name=model_name,
        groq_api_key=groq_api_key,
        temperature=temperature,
        max_retries=3,
        **kwargs
    )
