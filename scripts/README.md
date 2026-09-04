# Development scripts

These scripts are optional tools for manual testing and profiling. They are not
used by the application or CI pipeline.

## API CLI

Start the application, then install the script dependency and launch the
interactive client from the repository root:

```powershell
python -m pip install -r scripts/requirements.txt
python scripts/api_cli.py
```

## Engine profiler

Run the AlphaBeta profiling playground from the repository root using the
backend development environment:

```powershell
python scripts/profile_engine.py
```