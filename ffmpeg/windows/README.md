# FFmpeg

The FFmpeg binaries are intentionally **not included** in this repository.

This keeps the repository lightweight and avoids GitHub's file size limits.

During development, place the appropriate FFmpeg binaries in this directory:

Windows:
- ffmpeg.exe
- ffprobe.exe

Linux:
- ffmpeg
- ffprobe

When building releases with GitHub Actions, these binaries are downloaded automatically and bundled with the application.