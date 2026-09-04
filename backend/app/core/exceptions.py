from fastapi import status


class BukochessException(Exception):
    """
    Base exception for controlled errors in the application.
    """

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class LLMProviderException(Exception):
    """A safe, provider-independent error raised while choosing an LLM move."""

    def __init__(self, code: str, message: str, *, retryable: bool):
        self.code = code
        self.message = message
        self.retryable = retryable
        super().__init__(message)


class LLMMaxOutputTokensException(LLMProviderException):
    """Raised when an LLM stops before returning a move due to its token limit."""

    def __init__(self, provider: str):
        super().__init__(
            "max_output_tokens",
            f"{provider} reached the maximum output-token limit before "
            "returning a move.",
            retryable=True,
        )
