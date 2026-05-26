# Быстрый помощник для Bitrix (без сложностей)

## Запуск за 1 команду

```bash
./quick_start.sh
```

После запуска открой:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs` (удобная форма, чтобы сразу добавить встречу)

## Самый быстрый сценарий: прямо тут, без Bitrix

Добавь встречу через Swagger (`/docs`) в методе `POST /quick/add` или командой:

```bash
curl -X POST http://127.0.0.1:8000/quick/add \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "ООО Ромашка",
    "chat_id": "my-chat",
    "text": "созвон по договору",
    "meeting_at": "2026-05-27T15:00:00+03:00"
  }'
```

Напоминание придёт в лог сервиса (`[REMINDER] ...`).

## Подключение Bitrix (когда будешь готов)

1. В Bitrix настрой исходящий webhook на `POST /bitrix/events`.
2. Если нужно, задай секрет в `.env` (`BITRIX_WEBHOOK_SECRET`) и передавай заголовок `X-Webhook-Secret`.
3. Чтобы отправлять сообщения обратно в Bitrix, укажи `BITRIX_OUTGOING_WEBHOOK_URL`.

## Настройки

Файл `.env`:
- `BITRIX_WEBHOOK_SECRET=change_me`
- `BITRIX_OUTGOING_WEBHOOK_URL=...` (можно оставить пустым для быстрого режима)
- `TIMEZONE=Europe/Moscow`
- `REMINDER_MINUTES_BEFORE=30`
