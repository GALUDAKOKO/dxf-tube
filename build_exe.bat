@echo off
chcp 65001 >nul
echo ============================================
echo  DXF Tube — Build EXE
echo ============================================

cd /d "%~dp0"

echo [1/3] Installing dependencies...
py -m pip install -r requirements.txt pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: pip install failed
    pause & exit /b 1
)

echo [2/3] Running PyInstaller...
py -m PyInstaller ^
  --onefile ^
  --noconsole ^
  --name "dxf-tube-app" ^
  --add-data "app/index.html;app" ^
  --add-data "app/server.py;app" ^
  --add-data "app/dxf_tube.py;app" ^
  --hidden-import uvicorn.logging ^
  --hidden-import uvicorn.loops ^
  --hidden-import uvicorn.loops.auto ^
  --hidden-import uvicorn.protocols ^
  --hidden-import uvicorn.protocols.http ^
  --hidden-import uvicorn.protocols.http.auto ^
  --hidden-import uvicorn.protocols.websockets ^
  --hidden-import uvicorn.protocols.websockets.auto ^
  --hidden-import uvicorn.lifespan ^
  --hidden-import uvicorn.lifespan.on ^
  --hidden-import fastapi ^
  --hidden-import anyio ^
  --hidden-import starlette ^
  --hidden-import pandas ^
  --hidden-import openpyxl ^
  --hidden-import ezdxf ^
  main.py

if errorlevel 1 (
    echo ERROR: PyInstaller failed
    pause & exit /b 1
)

echo [3/3] Copying exe to parent folder...
copy /Y "dist\dxf-tube-app.exe" "..\dxf-tube-app.exe"

echo.
echo ============================================
echo  DONE! File saved to:
echo  %~dp0..\dxf-tube-app.exe
echo  Double-click to run — browser opens auto.
echo ============================================
pause
