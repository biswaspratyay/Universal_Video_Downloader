# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import platform

block_cipher = None

# ==========================================================
# Project Root
# ==========================================================

project_root = Path(SPECPATH).resolve()

assets_dir = project_root / "assets"
ffmpeg_root = project_root / "ffmpeg"

system = platform.system()

# ==========================================================
# Platform-specific resources
# ==========================================================

if system == "Windows":
    icon_file = assets_dir / "icons" / "app.ico"
    ffmpeg_dir = ffmpeg_root / "windows"

elif system == "Linux":
    icon_file = assets_dir / "icons" / "app.png"
    ffmpeg_dir = ffmpeg_root / "linux"

else:
    icon_file = assets_dir / "icons" / "app.png"
    ffmpeg_dir = ffmpeg_root

# ==========================================================
# Data Files
# ==========================================================

datas = []

if assets_dir.exists():
    datas.append((str(assets_dir), "assets"))

if ffmpeg_dir.exists():
    # Bundle only the current platform's FFmpeg
    datas.append((str(ffmpeg_dir), "ffmpeg"))

# ==========================================================
# Analysis
# ==========================================================

a = Analysis(
    ["main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooks=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ==========================================================
# PYZ
# ==========================================================

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# ==========================================================
# Executable
# ==========================================================

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="UniversalVideoDownloader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(icon_file) if icon_file.exists() else None,
)

# ==========================================================
# Collect
# ==========================================================

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="UniversalVideoDownloader",
)
