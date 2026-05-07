#!/bin/bash
set -e

cd /workspace/frontend
npm install

cd /workspace/backend
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
