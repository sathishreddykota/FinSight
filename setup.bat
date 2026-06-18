@echo off
REM Quick Setup Script for FinSight on Windows

echo.
echo ========================================
echo FinSight - Quick Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11+ not found. Please install from python.org
    pause
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js 18+ not found. Please install from nodejs.org
    pause
    exit /b 1
)

REM Setup Python venv
echo.
echo [1/5] Setting up Python virtual environment...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

REM Install Python deps
echo [2/5] Installing Python dependencies...
pip install -q -r requirements.txt
pip install -q -r backend\agent\requirements.txt

REM Setup .env
if not exist .env (
    echo [3/5] Creating .env file...
    copy .env.example .env
    echo.
    echo NOTE: Edit .env and add your GROQ_API_KEY
    echo   Get one free at https://console.groq.com
    echo.
    pause
)

REM Setup frontend
echo [4/5] Setting up frontend dependencies...
cd frontend
call npm install -q
cd ..

REM Start Qdrant
echo.
echo [5/5] Starting Qdrant vector database...
echo   Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo   Docker not found. Please install Docker Desktop
    echo   https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker run -d -p 6333:6333 -p 6334:6334 --name qdrant-finsight qdrant/qdrant:latest >nul 2>&1
if errorlevel 0 (
    echo   ✓ Qdrant started
) else (
    echo   Qdrant already running
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run indexing (takes 2-3 hours):
echo    python backend\ingestion\indexer.py
echo.
echo 2. In a new terminal, start backend:
echo    venv\Scripts\activate
echo    uvicorn backend.api.main:app --reload --port 8000
echo.
echo 3. In another terminal, start frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 4. Open browser to http://localhost:3000
echo.
pause
