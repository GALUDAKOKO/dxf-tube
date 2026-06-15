#!/usr/bin/env python3
"""
dxf_tube — launcher entry point for PyInstaller exe.

Opens the browser automatically then starts uvicorn.
"""
import os
import sys
import threading
import time
import webbrowser

# ── locate bundled files when running as a frozen exe ──────────────────────
if getattr(sys, "frozen", False):
    BASE = sys._MEIPASS  # type: ignore[attr-defined]
else:
    BASE = os.path.dirname(os.path.abspath(__file__))

# Make sure app/ modules can be found
APP_DIR = os.path.join(BASE, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# ── fix stdout/stderr=None when running as --noconsole exe ─────────────────
import io
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

HOST = "127.0.0.1"
PORT = 8765          # different from 8000 to avoid conflicts
URL  = f"http://{HOST}:{PORT}"


def _open_browser():
    time.sleep(1.5)   # give uvicorn a moment to start
    webbrowser.open(URL)


if __name__ == "__main__":
    threading.Thread(target=_open_browser, daemon=True).start()

    import uvicorn
    # import the FastAPI app object that lives in app/server.py
    from server import app as fastapi_app  # noqa: E402

    uvicorn.run(fastapi_app, host=HOST, port=PORT, log_level="warning")
