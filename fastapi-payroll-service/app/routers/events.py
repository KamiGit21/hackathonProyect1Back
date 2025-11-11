from fastapi import APIRouter, Request, Header, HTTPException
from app.config import settings
from app.repos.payroll_repo import add_event
from typing import Dict, Any
import json

router = APIRouter()

@router.post("/events")
async def receive_event(request: Request, x_push_token: str | None = Header(None)):
    """
    Generic event receiver for TIME/LEAVE events.
    If Pub/Sub push is used, configure the push subscription to forward the message body (JSON).
    Optional simple verification via header 'x-push-token' if you set PUBSUB_PUSH_VERIFICATION_TOKEN.
    Expected body:
    {
      "event": "LeaveApproved" | "TimeAbsent",
      "employee_uid": "...",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",  # optional
      "justified": false,        # for TimeAbsent
      ...
    }
    """
    # optional verification
    if settings.pubsub_push_verification_token:
        if x_push_token != settings.pubsub_push_verification_token:
            raise HTTPException(status_code=403, detail="invalid push token")
    body = await request.json()
    # Normalize pubsub push envelope if present (GCP Pub/Sub push wraps message)
    # e.g. { "message": { "data":"base64", "attributes": {...} } }
    if "message" in body and "data" in body["message"]:
        import base64
        raw = base64.b64decode(body["message"]["data"]).decode("utf-8")
        try:
            body = json.loads(raw)
        except Exception:
            body = {"raw": raw}
    # attach received_at
    body["received_at"] = int(datetime.utcnow().timestamp())
    add_event(body)
    return {"status":"ok", "stored": True}