@echo off
REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo Launching with virtual environment...
    .venv\Scripts\python.exe app.py
) else (
    echo Virtual environment not found. Launching with system python...
    py -3.12 app.py
)
pause
