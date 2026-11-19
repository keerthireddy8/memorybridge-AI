from fastapi import APIRouter
from backend.models import PrivacyZoneToggleRequest
from backend.services.privacy_engine import get_zone_statuses, toggle_zone_privacy
from backend.services.vision_engine import vision_service

router = APIRouter(prefix="/api/privacy", tags=["privacy"])

@router.get("/zones")
def read_zones():
    return get_zone_statuses()

@router.post("/zones/{location_id}/toggle")
def toggle_zone(location_id: str, req: PrivacyZoneToggleRequest):
    toggle_zone_privacy(location_id, req.privacy_mode)
    if location_id in ["loc_bedroom", "loc_bathroom"]:
        vision_service.set_privacy_mode(req.privacy_mode == 1)
    return {"location_id": location_id, "privacy_mode": req.privacy_mode, "success": True}
