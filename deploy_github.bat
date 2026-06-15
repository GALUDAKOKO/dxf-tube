@echo off
echo === DXF-Tube: Push to GitHub ===
cd /d "C:\Users\galud\Downloads\รวมเอกสาร\AI_PRODUCT\CAD_TUBE\APP\dxf-tube-app"

git init
git add .
git commit -m "initial: dxf-tube FastAPI app"
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/GALUDAKOKO/dxf-tube.git
git push -u origin main

echo.
echo === Done! ===
echo Repo: https://github.com/GALUDAKOKO/dxf-tube
pause
