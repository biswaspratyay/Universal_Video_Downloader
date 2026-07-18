# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

block_cipher = None

project_root = Path.cwd()
ffmpeg_dir = project_root / "ffmpeg"
assets_dir = project_root / "assets"

added_files = []
if ffmpeg_dir.exists():
    added_files.append((str(ffmpeg_dir), "ffmpeg"))
if assets_dir.exists():
    added_files.append((str(assets_dir), "assets"))


a = Analysis(
    ["main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=added_files,
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    icon=str(project_root / "assets" / "icons" / "app.ico"),
)

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
