import os


def get_llm(temperature: float = 0):
    provider = os.getenv("LLM_PROVIDER", "google").lower()

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_MODEL", "gemini-2.5-flash"),
            temperature=temperature,
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
            temperature=temperature,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER: {provider!r}. Expected 'google' or 'anthropic'."
    )
