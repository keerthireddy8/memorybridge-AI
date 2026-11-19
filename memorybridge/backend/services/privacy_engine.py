from backend.database import get_db_connection

def is_private_zone(location_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT zone_type, privacy_mode FROM locations WHERE id = ?", (location_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row["zone_type"] == "private" and row["privacy_mode"] == 1:
        return True
    return False

def get_zone_statuses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, zone_type, privacy_mode, description FROM locations ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    zones = []
    for r in rows:
        zones.append({
            "id": r["id"],
            "name": r["name"],
            "zone_type": r["zone_type"],
            "privacy_mode": r["privacy_mode"],
            "status_label": "Privacy Mode Active" if (r["zone_type"] == "private" and r["privacy_mode"] == 1) else "Visual Observation Active",
            "observation_allowed": not (r["zone_type"] == "private" and r["privacy_mode"] == 1),
            "description": r["description"]
        })
    return zones

def toggle_zone_privacy(location_id: str, privacy_mode: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE locations SET privacy_mode = ? WHERE id = ?", (privacy_mode, location_id))
    conn.commit()
    conn.close()
    return True
