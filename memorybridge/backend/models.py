from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UserSchema(BaseModel):
    id: str
    name: str
    role: str
    created_at: str

class LocationSchema(BaseModel):
    id: str
    name: str
    zone_type: str  # 'activity' or 'private'
    privacy_mode: int  # 1 = active, 0 = disabled
    description: Optional[str] = None

class ObjectSchema(BaseModel):
    id: str
    name: str
    category: str
    current_location_id: Optional[str] = None
    last_observed_at: Optional[str] = None

class EventCreateSchema(BaseModel):
    user_id: str = "user_01"
    object_id: Optional[str] = None
    action: str
    location_id: str
    confidence: float = 0.95
    verification_status: str = "VERIFIED"  # 'VERIFIED', 'INFERRED', 'UNCERTAIN'
    privacy_status: str = "PUBLIC"         # 'PUBLIC', 'BOUNDARY_CROSSED', 'ZONE_MASKED'
    description: str
    metadata: Optional[Dict[str, Any]] = None

class EventResponseSchema(BaseModel):
    id: str
    user_id: str
    object_id: Optional[str] = None
    object_name: Optional[str] = None
    action: str
    location_id: str
    location_name: Optional[str] = None
    zone_type: Optional[str] = None
    timestamp: str
    display_time: str
    confidence: float
    verification_status: str
    privacy_status: str
    description: str
    metadata: Optional[str] = None

class AskMemoryRequest(BaseModel):
    query: str

class AskMemoryResponse(BaseModel):
    query: str
    answer: str
    matched_object: Optional[str] = None
    matched_location: Optional[str] = None
    observed_time: Optional[str] = None
    verification_status: str
    confidence: float
    is_private_zone: bool
    explanation: str
    relevant_events: List[EventResponseSchema] = []

class RoutineStepSchema(BaseModel):
    step_order: int
    activity: str
    location_name: str
    typical_time: str
    notes: Optional[str] = None

class RoutineDeviationResponse(BaseModel):
    is_deviated: bool
    status_label: str
    summary_message: str
    normal_sequence: List[str]
    current_sequence: List[str]
    deviation_points: List[str]
    timestamp: str
    advice: str

class PrivacyZoneToggleRequest(BaseModel):
    privacy_mode: int

class DemoSimulateRequest(BaseModel):
    scenario: str  # 'key_pickup', 'key_bedroom_move', 'medicine_repeat', 'routine_normal', 'routine_deviation', 'reset'
