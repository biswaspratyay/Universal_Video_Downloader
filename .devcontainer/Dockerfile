FROM mcr.microsoft.com/devcontainers/python:3.12

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libegl1 \
    libgl1 \
    libxcb-cursor0 \
    patchelf \
    desktop-file-utils \
    fuse \
    && rm -rf /var/lib/apt/lists/*