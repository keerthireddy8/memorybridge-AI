from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.models import EventCreateSchema, EventResponseSchema
from backend.services.event_engine import record_event, get_recent_events, search_events_by_object
from backend.services.anchor_engine import check_medicine_anchor

router = APIRouter(prefix="/api/events", tags=["events"])

@router.get("", response_model=List[EventResponseSchema])
def list_events(limit: int = Query(50, ge=1, le=200), user_id: str = "user_01"):
    return get_recent_events(limit=limit, user_id=user_id)

@router.post("", response_model=EventResponseSchema)
def create_event(event_in: EventCreateSchema):
    try:
        created = record_event(
            user_id=event_in.user_id,
            action=event_in.action,
            location_id=event_in.location_id,
            object_id=event_in.object_id,
            confidence=event_in.confidence,
            verification_status=event_in.verification_status,
            privacy_status=event_in.privacy_status,
            description=event_in.description,
            metadata=event_in.metadata
        )
        return created
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[EventResponseSchema])
def search_events(q: str):
    return search_events_by_object(q)

@router.get("/anchor/medicine")
def get_medicine_anchor(user_id: str = "user_01"):
    return check_medicine_anchor(user_id=user_id)
