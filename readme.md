# bukochess ♟️

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Language-Python%203.10%2B-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Testing-Pytest-0E7FBF?style=flat-square&logo=pytest)](https://docs.pytest.org/)

**bukochess** goal is to become a high-performance chess ecosystem built from the ground up. This is a longterm project of a chess enthusiast and software-nerd.

The core philosophy is **Zero Dependencies**: All chess rules, move generation (bitboards/mailbox), and engine heuristics are implemented from scratch.

## Key Engineering Highlights

* **Custom Move Generator:** Implemented a Mailbox system that can handle~50k nodes/sec in pure Python.
* **Engine Intelligence:** Minimax-based engine with alpha-beta pruning, capable of defeating intermediate players.
* **Perft Validated:** Move generation accuracy is rigorously verified against standard Perft (Performance Test) suites.
* **Clean Architecture:** Strict separation between domain logic, API delivery (FastAPI), and CLI clients.

---

## 🏗️ Project Structure

The repository is organized as a monorepo to demonstrate full-stack/end-to-end responsibility:

* **/backend**: (Beta) The core engine and service layer.
    * `chess/`: Move generation, rule validation, and engine logic.
    * `api/`: FastAPI endpoints and REST resource definitions.
    * `core/`: Infrastructure concerns (logging, global exception handlers).
* **/cli**: A standalone Python client that interfaces with the backend via HTTP.
    * this just served as a POC
* **/frontend**: (Alpha) React-based frontend for visual gameplay.

---

## 🕹️ Getting Started

### 1. Backend & API
The backend provides a RESTful interface and auto-generated Swagger documentation.

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API: http://127.0.0.1:8000

Docs (Swagger): http://127.0.0.1:8000/docs

**Running tests:**

From the backend folder, run:
```bash
    pytest -v 
```

## CLI UI

The CLI is a separate Client that talks to the backend via HTTP.
First start the backend:
```
    cd backend
    uvicorn app.main:app --reload
```
Start the CLI:
```
    cd cli
    python main.py
```
## Status / milestones

- created API 
- implemented chess rules
- implemented perft and perft divide functions
- tested a lot of positions with perft
- added first "engine" "random" (just returns random moves, no valuation)
- added CLI GUI
- added POC UI
- added second engine "dumb": Algorithm: MINIMAX in Python. Can checkmate intermediate beginners
- added mailbox logic and bitwise operators. Movegenerator hits almost 50k nodes per second