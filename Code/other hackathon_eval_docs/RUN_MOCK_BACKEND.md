# Run Mock FastAPI Backend

Run these commands from the project root (where `mock_deals_backend.py` and `mock_during_call_backend.py` live).

To run the deals mock backend:

```powershell
uvicorn mock_deals_backend:app --reload --port 8000
```

To run the during-call mock backend:

```powershell
uvicorn mock_during_call_backend:app --reload --port 8000
```

If you prefer a single entrypoint, create `main.py` that imports one of the mock apps and exposes it as `app` (example below), then run `uvicorn main:app`.

Example `main.py`:

```python
from fastapi import FastAPI
from mock_deals_backend import app as deals_app

app = FastAPI()
app.mount("/", deals_app)
```

Notes:
- Make sure your virtual environment is active and dependencies from `requirements.txt` are installed.
- If you see "Could not import module \"main\"", point `uvicorn` to an existing module that exposes `app` (for example `mock_deals_backend:app`).
