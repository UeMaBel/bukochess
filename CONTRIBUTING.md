Bukochess follows a lightweight branching workflow:

## Permanent branches

- main – Always stable. Production-ready snapshots only.

- development – Active development branch. Features merge here first.

## Temporary branches

Create a new branch for every feature or fix:

- feature/<name>   – New features
- fix/<name>       – Bug fixes
- refactor/<name>  – Structural improvements, no behavior changes
- docs/<name>      – Documentation updates


**Examples:**

- feature/movegen
- feature/api-websocket
- fix/fen-parsing
- refactor/board-representation
- docs/architecture-overview

## Commit Message Guidelines

Bukochess uses a conventional commit format:

- type(scope): short description

## Types:

- feat – New feature

- fix – Bug fix

- refactor – Code restructuring

- docs – Documentation only

- test – Tests

- chore – CI/CD, configs, maintenance

**Examples:**
- feat(movegen): implement bishop slider logic
- fix(fen): correct en passant square parsing
- refactor(core): simplify board representation
- docs(readme): add project overview
- chore(ci): add GitLab pipeline
- test(perft): add depth 5 perft test

Do not commit directly to main.

## Branch & Merge Workflow
**Starting a new feature:**
- git checkout development
- git pull
- git checkout -b feature/<name>

**After coding:**
- git add .
- git commit -m "feat(engine): add basic evaluation function"
- git push -u origin feature/<name>

**Merging back into development:**
- git checkout development
- git pull
- git merge feature/<name>
- git push

**Release milestone → merge into main:**
- git checkout main
- git merge development
- git push

## Tagging Releases

**Tag important milestones and versions:**

- git tag -a v0.1 -m "Initial FastAPI backend skeleton"
- git push origin v0.1