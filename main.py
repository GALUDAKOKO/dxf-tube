#!/usr/bin/env python3
"""
DXF Tube — EXE launcher
Auto-opens browser and starts FastAPI server on port 8000.
"""
import io
import os
import sys
import threading
import time
import webbrowser

# ── Fix stdout/stderr = None in --noconsole frozen exe (CRITICAL) ──
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# ── Locate bundled files when frozen ──
if getattr(sys, "frozen", False):
    BASE = sys._MEIPASS
else:
    BASE = os.path.dirname(os.path.abspath(__file__))

APP_DIR = os.path.join(BASE, "app")
if os.path.isdir(APP_DIR) and APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if BASE not in sys.path:
    sys.path.insert(0, BASE)

HOST = "127.0.0.1"
PORT = 8000
URL  = f"http://{HOST}:{PORT}"


def _open_browser():
    time.sleep(1.5)
    webbrowser.open(URL)


if __name__ == "__main__":
    threading.Thread(target=_open_browser, daemon=True).start()
    import uvicorn
    from server import app as fastapi_app
    uvicorn.run(fastapi_app, host=HOST, port=PORT, log_level="warning")
