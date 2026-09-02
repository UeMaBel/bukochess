# AGENTS.md

## Project
BukoChess is a React + TypeScript frontend with a FastAPI backend. Keep changes focused, readable, and compatible with the existing engine architecture.

## General
- Do not refactor unrelated code unless necessary.
- Prefer small functions, explicit names, and simple abstractions.
- Preserve existing behavior unless the task explicitly changes it.
- Keep secrets and API keys out of source control.
- Run relevant tests/checks after changes.

## Backend
- `app/api/` handles HTTP only: validate input, delegate work, return responses.
- `app/chess/engines/` contains chess engines and shared engine models.
- `app/ai/` contains LLM settings, provider interfaces, provider integrations, and AI models.
- Chess rules, legal moves, FEN handling, and board state remain authoritative in the chess layer.
- LLM providers may choose a move, but the chess layer must validate it.
- All engines implement the common `Engine` interface.
- `choose_move()` returns an `EngineResult`; avoid hidden result state on engine instances.
- Engine-specific diagnostics belong in `EngineResult.metadata`.
- API requests keep `fen` and `engine` top-level; engine-specific settings belong in `metadata`.
- Prefer Pydantic for validated/serialized boundary models.
- Use Python type hints and snake_case.
- Keep provider-specific SDK code out of `llm_engine.py`.
- Convert external provider errors into project-specific exceptions.
- Preserve AlphaBeta correctness before optimizing.
- For board/hash changes, verify apply/undo symmetry.

## Frontend
- `src/api/` contains API contracts, engine types, and saved settings models.
- Components handle UI/state; API details stay out of presentation components.
- Use typed engine-specific metadata and discriminated unions.
- Avoid `any` and `metadata["..."]` when a typed structure can be used.
- Keep White and Black engine/AI settings independent.
- Reuse typed settings objects instead of adding many individual props.
- `AIPlayerSettings` is the metadata sent for an LLM engine request.
- Keep settings separate from response diagnostics.
- Reuse existing CSS patterns and preserve the chessboard as the visual focus.
- Keep controls compact, aligned, and responsive.
- Remove temporary `console.log` calls after debugging.
- Inspect browser Network payloads when debugging API validation errors.

## Validation
- Backend: run relevant pytest tests.
- Frontend: run TypeScript/Vite checks when dependencies are available.
- Test Random, Dumb, AlphaBeta, and LLM request construction separately.
