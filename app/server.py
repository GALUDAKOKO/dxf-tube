#!/usr/bin/env python3
"""
DXF Tube — local web app.

Run:
    pip install -r requirements.txt
    python app/server.py
Then open http://127.0.0.1:8000 in a browser, upload a .dxf, click Export.

The DXF is parsed in memory and an .xlsx is streamed straight back to the
browser as a download. Nothing is stored on disk.
"""
import io
import os
import sys
import tempfile

# Ensure app/ directory is in path (needed when running from project root on Render)
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse

import dxf_tube  # the tested engine, unchanged

app = FastAPI(title="DXF Tube")

HERE = os.path.dirname(os.path.abspath(__file__))


@app.get("/", response_class=HTMLResponse)
def index():
    with open(os.path.join(HERE, "index.html"), encoding="utf-8") as f:
        return f.read()


@app.post("/export")
async def export(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".dxf"):
        raise HTTPException(status_code=400, detail="กรุณาอัปโหลดไฟล์ .dxf เท่านั้น")

    data = await file.read()
    # ezdxf reads from a path; write the upload to a temp file then parse.
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        xlsx_bytes, stats = dxf_tube.build_workbook_bytes(tmp_path)
    except Exception as e:  # noqa: BLE001 — surface parse errors to the UI
        raise HTTPException(status_code=422, detail=f"อ่านไฟล์ DXF ไม่สำเร็จ: {e}")
    finally:
        os.unlink(tmp_path)

    out_name = os.path.splitext(file.filename)[0] + "_tube_list.xlsx"
    headers = {
        "Content-Disposition": f'attachment; filename="{out_name}"',
        # expose stats to the JS so it can show a summary
        "X-Tube-Stats": f"{stats['marks']},{stats['traced']},{stats['blank']},{stats['devices']}",
        "Access-Control-Expose-Headers": "X-Tube-Stats, Content-Disposition",
    }
    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1"
    uvicorn.run(app, host=host, port=port)
