import os
from typing import Any, Optional
from dotenv import load_dotenv
from pydantic import SecretStr

# Load .env file variables into os.environ
load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "google").lower()

def get_llm(model: Optional[str] = None, temperature: float = 0.2, **kwargs: Any):
    """
    Single source of truth for LLM construction.
    Uses SecretStr to satisfy pydantic type safety requirements.
    """

    # ------------------------
    # Google Gemini
    # ------------------------
    if PROVIDER == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        raw_api_key = os.getenv("GOOGLE_API_KEY")
        if not raw_api_key:
            raise ValueError("GOOGLE_API_KEY not set in .env")

        return ChatGoogleGenerativeAI(
            model=model or "gemini-2.0-flash",
            api_key=SecretStr(raw_api_key),
            temperature=temperature,
            **kwargs
        )

    # ------------------------
    # OpenAI
    # ------------------------
    elif PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        raw_api_key = os.getenv("OPENAI_API_KEY")
        if not raw_api_key:
            raise ValueError("OPENAI_API_KEY not set in .env")

        return ChatOpenAI(
            model=model or "gpt-4o-mini",
            api_key=SecretStr(raw_api_key),
            temperature=temperature,
            **kwargs
        )

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {PROVIDER}")

if __name__ == "__main__":
    # Quick sanity check
    try:
        llm = get_llm()
        print(f"✅ Successfully initialized {PROVIDER} LLM")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
