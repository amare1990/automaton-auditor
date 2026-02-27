import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    TEMP: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    OPENAI_KEY: str | None = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")


settings = Settings()
