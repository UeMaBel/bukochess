from fastapi import status


class BukochessException(Exception):
    """
    Base exception for controlled errors in the application.
    """

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
