$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
python -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
& '.\.venv\Scripts\python.exe' -m unittest -v test_core.py
if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
& '.\.venv\Scripts\python.exe' -m PyInstaller --noconfirm --clean --onefile --windowed --name NeteaseConverter --collect-all _soundfile_data --exclude-module matplotlib --exclude-module scipy --exclude-module pandas --exclude-module PIL --exclude-module pytest --exclude-module IPython app.py
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
Write-Output 'Created dist\NeteaseConverter.exe'
