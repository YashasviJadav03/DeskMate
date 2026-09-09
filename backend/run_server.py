import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("[DeskMate] FastAPI Backend running!", flush=True)
    print("  -> API Docs:  http://127.0.0.1:8000/docs", flush=True)
    print("  -> Frontend:  http://127.0.0.1:5173", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
