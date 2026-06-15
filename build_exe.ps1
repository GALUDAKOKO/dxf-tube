# build_exe.ps1 — Build dxf_tube.exe with PyInstaller
# Run: .\build_exe.ps1   (in the dxf-tube-app folder)

$ErrorActionPreference = "Stop"
$AppDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$OutputDir = "C:\Users\galud\Downloads\รวมเอกสาร\AI_PRODUCT\CAD_TUBE\APP"

Set-Location $AppDir
Write-Host "=== Installing dependencies ===" -ForegroundColor Cyan
py -m pip install -r requirements.txt pyinstaller --quiet

Write-Host "=== Building exe ===" -ForegroundColor Cyan
py -m PyInstaller `
    --onefile `
    --noconsole `
    --name "dxf_tube" `
    --add-data "app/index.html;app" `
    --add-data "app/dxf_tube.py;app" `
    --add-data "app/server.py;app" `
    --hidden-import "uvicorn.logging" `
    --hidden-import "uvicorn.loops" `
    --hidden-import "uvicorn.loops.auto" `
    --hidden-import "uvicorn.protocols" `
    --hidden-import "uvicorn.protocols.http" `
    --hidden-import "uvicorn.protocols.http.auto" `
    --hidden-import "uvicorn.protocols.websockets" `
    --hidden-import "uvicorn.protocols.websockets.auto" `
    --hidden-import "uvicorn.lifespan" `
    --hidden-import "uvicorn.lifespan.on" `
    --hidden-import "fastapi" `
    --hidden-import "anyio" `
    --hidden-import "starlette" `
    --hidden-import "ezdxf" `
    --hidden-import "pandas" `
    --hidden-import "openpyxl" `
    main.py

Write-Host "=== Copying to output folder ===" -ForegroundColor Cyan
$src = Join-Path $AppDir "dist\dxf_tube.exe"
$dst = Join-Path $OutputDir "dxf_tube.exe"
Copy-Item -Force $src $dst

Write-Host ""
Write-Host "✅ สำเร็จ! ไฟล์อยู่ที่:" -ForegroundColor Green
Write-Host "   $dst" -ForegroundColor Yellow
