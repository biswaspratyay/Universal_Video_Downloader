@echo off
cd /d "%~dp0"
.venv\Scripts\python.exe -m PyInstaller --noconfirm --log-level=WARN UniversalVideoDownloader.spec > build\pyinstaller-release.log 2>&1
