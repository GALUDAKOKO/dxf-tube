@echo off
chcp 65001 >nul
echo ============================================
echo  DXF Tube — Push ver2 to GitHub
echo ============================================

cd /d "%~dp0"

echo [1/4] git init (ถ้ายังไม่มี)...
git init

echo [2/4] Add remote (ข้ามถ้ามีอยู่แล้ว)...
git remote add origin https://github.com/galuda25923/dxf-tube.git 2>nul
git remote set-url origin https://github.com/galuda25923/dxf-tube.git

echo [3/4] Commit all changes...
git add .
git commit -m "ver2: Render-ready, PORT env, sys.path fix"

echo [4/4] Push to branch ver2...
git push -u origin HEAD:ver2

echo.
echo DONE! Branch ver2 pushed to:
echo https://github.com/galuda25923/dxf-tube/tree/ver2
echo.
echo ถัดไป: ไปที่ Render dashboard → service dxf-tube
echo        Settings → Branch → เปลี่ยนเป็น ver2 → Manual Deploy
pause
