@echo off
chcp 65001 > nul
echo =========================================
echo ?? BACKEND API ?? ????
echo =========================================
echo.
cd /d "%~dp0"
echo ?? ?????: %cd%
echo.
echo ?? ????? ???...
echo   ?????: http://localhost:8000
echo   Docs:  http://localhost:8000/docs
echo   Health: http://localhost:8000/health
echo   Lottery: http://localhost:8000/api/v1/lottery/health
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
