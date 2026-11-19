from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.services.vision_engine import vision_service

router = APIRouter(prefix="/api/vision", tags=["vision"])

@router.get("/stream")
def video_stream():
    """
    Returns live multipart/x-mixed-replace stream for browser <img> tags.
    Applies real-time privacy blind when privacy mode is engaged.
    """
    return StreamingResponse(
        vision_service.generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/status")
def vision_status():
    return {
        "camera_detected": vision_service.is_camera_open,
        "privacy_mode_active": vision_service.privacy_mode_active,
        "tracked_target": vision_service.active_detected_object,
        "active_zone": vision_service.active_zone,
        "confidence": vision_service.confidence
    }
