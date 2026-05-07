FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Node and Python for the monorepo
RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*
RUN su vscode -c "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -"
RUN apt-get update && apt-get install -y nodejs python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

# Python tooling
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install poetry

WORKDIR /workspace
