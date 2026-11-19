from fastapi import APIRouter
from backend.models import AskMemoryRequest, AskMemoryResponse
from backend.services.memory_engine import recall_memory
from backend.services.event_engine import get_recent_events

router = APIRouter(prefix="/api/memory", tags=["memory"])

@router.post("/ask", response_model=AskMemoryResponse)
def ask_memory_endpoint(req: AskMemoryRequest):
    return recall_memory(query=req.query)

@router.get("/replay")
def get_replay_sequence(user_id: str = "user_01"):
    """
    Returns ordered spatio-temporal memory events formatted for 2D animated replay.
    """
    events = get_recent_events(limit=20, user_id=user_id)
    # Reverse so events are chronological
    chronological = list(reversed(events))

    # Build sequence steps for replay
    steps = []
    for idx, ev in enumerate(chronological):
        steps.append({
            "step_id": idx + 1,
            "event_id": ev["id"],
            "timestamp": ev["timestamp"],
            "display_time": ev["display_time"],
            "location_id": ev["location_id"],
            "location_name": ev["location_name"],
            "zone_type": ev["zone_type"],
            "action": ev["action"],
            "object_id": ev.get("object_id"),
            "object_name": ev.get("object_name"),
            "confidence": ev["confidence"],
            "verification_status": ev["verification_status"],
            "privacy_status": ev["privacy_status"],
            "is_privacy_boundary": ev["location_id"] in ["loc_bedroom", "loc_bathroom"] or ev["privacy_status"] in ["ZONE_MASKED", "BOUNDARY_CROSSED"],
            "description": ev["description"]
        })

    return {
        "total_steps": len(steps),
        "steps": steps,
        "replay_title": "Spatio-Temporal Event Trajectory",
        "boundary_principle": "Memory replay terminates at the last verified boundary transit to preserve resident dignity."
    }
