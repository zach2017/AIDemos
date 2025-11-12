@echo off
REM Quick start script for the Document Embeddings Builder (Windows)

echo Starting Document Embeddings Builder...
echo.
echo Installing dependencies (if needed)...
pip install -r requirements.txt --quiet

echo.
echo Starting Flask server...
echo Open your browser to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
