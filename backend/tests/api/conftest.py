import pytest
from fastapi.testclient import TestClient

from app.main import app


WHITE_START_FEN = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
)
BLACK_START_FEN = (
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(
    params=[
        pytest.param(("w", WHITE_START_FEN), id="white-to-move"),
        pytest.param(("b", BLACK_START_FEN), id="black-to-move"),
    ]
)
def engine_position(request: pytest.FixtureRequest) -> tuple[str, str]:
    return request.param


@pytest.fixture(
    params=[
        pytest.param(
            ("w", "8/8/8/8/8/7k/5q2/r6K w - - 0 1"),
            id="white-checkmated",
        ),
        pytest.param(
            ("b", "R6k/5Q2/7K/8/8/8/8/8 b - - 0 1"),
            id="black-checkmated",
        ),
    ]
)
def no_legal_moves_position(request: pytest.FixtureRequest) -> tuple[str, str]:
    return request.param
