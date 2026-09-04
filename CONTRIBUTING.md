# Contributing to BukoChess

BukoChess is primarily a personal learning and portfolio project, but bug
reports, suggestions, and focused pull requests are welcome.

## Branches

The repository has two permanent branches:

- `main` contains stable project snapshots.
- `development` is the integration branch for ongoing work.

Changes normally reach `main` through `development`.

Temporary branches often use a descriptive prefix such as `feature/`, `fix/`,
`refactor/`, `docs/`, or `tests/`. This is a preferred naming style rather than
a strictly enforced convention, and older branches do not always follow it.

## Making a change

Create a branch from `development` and keep the change focused. Before opening
a pull request, run the checks relevant to the area you changed.

Backend:

```powershell
cd backend
python -m ruff check .
python -m pytest
```

Frontend:

```powershell
cd frontend
npm run lint
npx tsc -b
npm test -- --run
```

For changes involving containers, also verify the Compose build from the
repository root:

```powershell
docker compose build
```

## Commits and pull requests

There is no strictly enforced commit-message format. Prefer a short imperative
summary that explains the outcome, for example:

```text
Fix promotion selection after board flip
Refactor frontend game state into hooks
Add CI checks for the backend
```

Pull requests should explain what changed, why it changed, and how it was
tested. Target `development` unless the change is specifically part of a
maintainer-managed release.

## Project expectations

- Keep changes focused and preserve existing behavior unless the change is
  intentional.
- Keep API keys, `.env` files, and other secrets out of source control.
- Add or update tests when behavior changes.
- Follow the existing backend and frontend architecture described in the
  project README.

GitHub Actions validates pushes to the permanent branches. Contributors should
run the relevant local checks before requesting a merge.
