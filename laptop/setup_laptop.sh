#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r laptop/requirements.txt
mkdir -p laptop/tts_cache
echo '완료. export OPENAI_API_KEY="sk-..." 를 설정하세요.'
