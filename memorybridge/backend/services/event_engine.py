import uuid
import json
from datetime import datetime
from backend.database import get_db_connection
from backend.services.privacy_engine import is_private_zone

def format_time_for_display(dt: datetime) -> str:
    # e.g., "2:15 PM"
    return dt.strftime("%I:%M %p").lstrip("0")

def record_event(
    user_id: str,
    action: str,
    location_id: str,
    object_id: str = None,
    confidence: float = 0.95,
    verification_status: str = "VERIFIED",
    privacy_status: str = "PUBLIC",
    description: str = None,
    metadata: dict = None,
    custom_time: datetime = None
) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()

    event_id = f"evt_{uuid.uuid4().hex[:8]}"
    now = custom_time if custom_time else datetime.now()
    timestamp_iso = now.isoformat()
    display_time = format_time_for_display(now)

    # Check privacy zone status
    private_zone = is_private_zone(location_id)
    if private_zone:
        privacy_status = "ZONE_MASKED" if action != "entered" else "BOUNDARY_CROSSED"

    # Fetch object name & location name for human-readable description if not provided
    cursor.execute("SELECT name FROM locations WHERE id = ?", (location_id,))
    loc_row = cursor.fetchone()
    loc_name = loc_row["name"] if loc_row else location_id

    obj_name = None
    if object_id:
        cursor.execute("SELECT name FROM objects WHERE id = ?", (object_id,))
        obj_row = cursor.fetchone()
        obj_name = obj_row["name"] if obj_row else object_id

    if not description:
        if private_zone:
            if object_id:
                description = f"{obj_name} was last confirmed entering the {loc_name} at {display_time}."
            else:
                description = f"Person entered {loc_name}. Visual observation paused at privacy boundary."
        else:
            if object_id:
                if action == "picked_up":
                    description = f"{obj_name} picked up in {loc_name}."
                elif action == "placed_on":
                    description = f"{obj_name} placed down in {loc_name}."
                elif action == "interacted_with":
                    description = f"{obj_name} interaction recorded in {loc_name}."
                else:
                    description = f"{obj_name} observed with action '{action}' in {loc_name}."
            else:
                description = f"Person {action} in {loc_name}."

    # Update object location if object_id is specified
    if object_id:
        cursor.execute(
            "UPDATE objects SET current_location_id = ?, last_observed_at = ? WHERE id = ?",
            (location_id, timestamp_iso, object_id)
        )

    metadata_json = json.dumps(metadata) if metadata else "{}"

    cursor.execute("""
        INSERT INTO events (
            id, user_id, object_id, action, location_id,
            timestamp, display_time, confidence, verification_status,
            privacy_status, description, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id, user_id, object_id, action, location_id,
        timestamp_iso, display_time, confidence, verification_status,
        privacy_status, description, metadata_json
    ))

    conn.commit()

    # Retrieve inserted event with joined details
    cursor.execute("""
        SELECT e.*, o.name as object_name, l.name as location_name, l.zone_type
        FROM events e
        LEFT JOIN objects o ON e.object_id = o.id
        LEFT JOIN locations l ON e.location_id = l.id
        WHERE e.id = ?
    """, (event_id,))
    created_row = dict(cursor.fetchone())
    conn.close()

    return created_row

def get_recent_events(limit: int = 50, user_id: str = "user_01") -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.*, o.name as object_name, l.name as location_name, l.zone_type
        FROM events e
        LEFT JOIN objects o ON e.object_id = o.id
        LEFT JOIN locations l ON e.location_id = l.id
        WHERE e.user_id = ?
        ORDER BY e.timestamp DESC
        LIMIT ?
    """, (user_id, limit))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def search_events_by_object(object_name_or_id: str) -> list:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.*, o.name as object_name, l.name as location_name, l.zone_type
        FROM events e
        LEFT JOIN objects o ON e.object_id = o.id
        LEFT JOIN locations l ON e.location_id = l.id
        WHERE (o.id LIKE ? OR LOWER(o.name) LIKE ? OR LOWER(e.description) LIKE ?)
        ORDER BY e.timestamp DESC
    """, (f"%{object_name_or_id}%", f"%{object_name_or_id.lower()}%", f"%{object_name_or_id.lower()}%"))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
