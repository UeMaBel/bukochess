# bukochess

**bukochess** is a personal chess project focused on:
- clean architecture
- testability
- engine experimentation
- multiple UIs (CLI, Web, etc.)
- optimization

The goal is **not** to use existing chess logic libraries — all chess rules, move generation, and engines are implemented from scratch.

## Structure

**backend**
- api: API Endpoints
- chess: Chess rules and engines
- core: logging, exception handlers, ...

**cli:**

commandline interface for playing chess


## Getting started

**Start the backend:**

    uvicorn app.main:app --reload

Backend will be available at:

Backend will be available at:

API: http://127.0.0.1:8000

Docs (Swagger): http://127.0.0.1:8000/docs

**Running tests:**

From the backend folder, run:

    pytest -v 


## CLI UI

The CLI is a separate Client that talks to the backend via HTTP.
First start the backend:

    cd backend
    uvicorn app.main:app --reload

Start the CLI:

    cd cli
    python main.py

## Status / milestones

- created API 
- implemented chess rules
- implemented perft and perft divide functions
- tested a lot of positions with perft
- added first "engine" "random" (just returns random moves, no valuation)
- added CLI GUI
- added POC UI