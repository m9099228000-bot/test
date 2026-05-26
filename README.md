# Ассистент для Bitrix: отслеживание клиентов + напоминания о встречах

Этот сервис принимает webhook-события из Bitrix24, сохраняет активность по клиентам и автоматически шлет напоминания о созвонах/встречах.

## Что умеет
- Принимает события сообщений клиентов (`/bitrix/events`).
- Фиксирует клиента, чат, текст последнего сообщения и время встречи.
- Ставит таймер и отправляет напоминание за `REMINDER_MINUTES_BEFORE` минут до встречи.

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload --port 8000
```

Проверка:

```bash
curl http://127.0.0.1:8000/health
```

## Пример события от Bitrix

```bash
curl -X POST http://127.0.0.1:8000/bitrix/events \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: change_me" \
  -d '{
    "client_id": "123",
    "client_name": "ООО Ромашка",
    "chat_id": "chat123",
    "text": "Давайте созвонимся завтра в 15:00",
    "created_at": "2026-05-26T10:00:00+03:00",
    "meeting_at": "2026-05-27T15:00:00+03:00"
  }'
```

## Как подключить к Bitrix24
1. В Bitrix создайте исходящий webhook/робот, который отправляет событие в `POST /bitrix/events`.
2. Передавайте заголовок `X-Webhook-Secret` для проверки.
3. Для отправки уведомлений назад в Bitrix укажите `BITRIX_OUTGOING_WEBHOOK_URL`.

## Важно
- Сейчас хранение данных в памяти процесса (для продакшна добавьте БД: PostgreSQL/Redis).
- При перезапуске приложения текущие встречи сбрасываются.
