from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
src = root / 'ffmpeg'
dist = root / 'dist' / 'UniversalVideoDownloader' / 'ffmpeg'

if src.exists():
    shutil.copytree(src, dist, dirs_exist_ok=True)
    print(f'Copied FFmpeg bundle to {dist}')
else:
    print('No ffmpeg folder found to copy')
