#!/usr/bin/env bash
set -e

python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
fi

echo "Готово. Запуск сервиса на http://127.0.0.1:8000"
exec uvicorn app:app --host 127.0.0.1 --port 8000
