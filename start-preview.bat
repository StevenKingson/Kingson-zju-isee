@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Local Python environment is missing. Please follow README.md.
  pause
  exit /b 1
)
echo Open http://127.0.0.1:8000/ in your browser.
echo Press Ctrl+C to stop the preview.
".venv\Scripts\python.exe" scripts\update-gallery.py
if errorlevel 1 (
  pause
  exit /b 1
)
".venv\Scripts\python.exe" scripts\update-music.py
if errorlevel 1 (
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m mkdocs serve -a 127.0.0.1:8000
pause
