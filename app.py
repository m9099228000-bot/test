from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
from typing import Dict

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from dateutil import parser as dt_parser
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Bitrix Client Tracker Assistant")

WEBHOOK_SECRET = os.getenv("BITRIX_WEBHOOK_SECRET", "")
BITRIX_API_URL = os.getenv("BITRIX_OUTGOING_WEBHOOK_URL", "")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")
REMINDER_MINUTES_BEFORE = int(os.getenv("REMINDER_MINUTES_BEFORE", "30"))

scheduler = BackgroundScheduler(timezone=TIMEZONE)
scheduler.start()

meetings: Dict[str, dict] = {}


class BitrixMessageEvent(BaseModel):
    client_id: str
    client_name: str
    chat_id: str
    text: str
    created_at: str
    meeting_at: str | None = None


def send_bitrix_notification(chat_id: str, message: str) -> None:
    if not BITRIX_API_URL:
        print(f"[DRY-RUN] chat={chat_id}: {message}")
        return

    payload = {
        "DIALOG_ID": chat_id,
        "MESSAGE": message,
    }
    url = f"{BITRIX_API_URL.rstrip('/')}/im.message.add.json"
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()



def reminder_job(client_id: str) -> None:
    record = meetings.get(client_id)
    if not record:
        return
    send_bitrix_notification(
        record["chat_id"],
        f"⏰ Напоминание: через {REMINDER_MINUTES_BEFORE} мин встреча с {record['client_name']} ({record['meeting_at']}).",
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "meetings": len(meetings)}


@app.post("/bitrix/events")
def bitrix_event(event: BitrixMessageEvent, x_webhook_secret: str = Header(default="")) -> dict:
    if WEBHOOK_SECRET and x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    meetings[event.client_id] = {
        "client_name": event.client_name,
        "chat_id": event.chat_id,
        "last_message": event.text,
        "created_at": event.created_at,
        "meeting_at": event.meeting_at,
    }

    send_bitrix_notification(
        event.chat_id,
        f"✅ Клиент {event.client_name} зафиксирован. Последнее сообщение: '{event.text[:80]}'",
    )

    if event.meeting_at:
        meeting_dt = dt_parser.parse(event.meeting_at)
        if meeting_dt.tzinfo is None:
            meeting_dt = meeting_dt.replace(tzinfo=ZoneInfo(TIMEZONE))

        reminder_time = meeting_dt - timedelta(minutes=REMINDER_MINUTES_BEFORE)
        job_id = f"reminder_{event.client_id}"

        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)

        if reminder_time > datetime.now(tz=meeting_dt.tzinfo):
            scheduler.add_job(reminder_job, "date", run_date=reminder_time, args=[event.client_id], id=job_id)

    return {"ok": True, "client_id": event.client_id}
