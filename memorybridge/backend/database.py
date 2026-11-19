import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "memorybridge.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'resident',
        created_at TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        zone_type TEXT NOT NULL, -- 'activity' or 'private'
        privacy_mode INTEGER NOT NULL DEFAULT 0, -- 1 = active, 0 = disabled
        description TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS objects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        current_location_id TEXT,
        last_observed_at TEXT,
        FOREIGN KEY (current_location_id) REFERENCES locations(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        object_id TEXT,
        action TEXT NOT NULL,
        location_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        display_time TEXT NOT NULL,
        confidence REAL NOT NULL DEFAULT 1.0,
        verification_status TEXT NOT NULL DEFAULT 'VERIFIED', -- 'VERIFIED', 'INFERRED', 'UNCERTAIN'
        privacy_status TEXT NOT NULL DEFAULT 'PUBLIC', -- 'PUBLIC', 'BOUNDARY_CROSSED', 'ZONE_MASKED'
        description TEXT NOT NULL,
        metadata TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (object_id) REFERENCES objects(id),
        FOREIGN KEY (location_id) REFERENCES locations(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS routines (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        step_order INTEGER NOT NULL,
        activity TEXT NOT NULL,
        location_id TEXT NOT NULL,
        typical_time TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (location_id) REFERENCES locations(id)
    );
    """)

    conn.commit()
    conn.close()

def seed_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    now_iso = datetime.now().isoformat()

    # Seed User
    cursor.execute(
        "INSERT INTO users (id, name, role, created_at) VALUES (?, ?, ?, ?)",
        ("user_01", "Eleanor Vance", "resident", now_iso)
    )

    # Seed Locations
    locations = [
        ("loc_living_room", "Living Room", "activity", 0, "Main communal area with sofa and coffee table"),
        ("loc_kitchen", "Kitchen", "activity", 0, "Meal prep area with refrigerator and medicine cabinet"),
        ("loc_dining", "Dining Area", "activity", 0, "Dining table and chairs"),
        ("loc_hallway", "Hallway", "activity", 0, "Central connecting passage"),
        ("loc_bedroom", "Bedroom", "private", 1, "Private sleeping and rest quarters"),
        ("loc_bathroom", "Bathroom", "private", 1, "Personal hygiene area - strict privacy")
    ]
    cursor.executemany(
        "INSERT INTO locations (id, name, zone_type, privacy_mode, description) VALUES (?, ?, ?, ?, ?)",
        locations
    )

    # Seed Tracked Objects
    objects = [
        ("obj_keys", "House Keys", "personal", "loc_living_room", now_iso),
        ("obj_glasses", "Reading Glasses", "personal", "loc_living_room", now_iso),
        ("obj_wallet", "Brown Wallet", "personal", "loc_hallway", now_iso),
        ("obj_medicine", "Morning Medicine Container", "health", "loc_kitchen", now_iso),
        ("obj_person", "Eleanor Vance", "person", "loc_living_room", now_iso)
    ]
    cursor.executemany(
        "INSERT INTO objects (id, name, category, current_location_id, last_observed_at) VALUES (?, ?, ?, ?, ?)",
        objects
    )

    # Seed Baseline Routine (Eleanor's typical morning)
    baseline_routines = [
        ("rt_1", "user_01", 1, "Wake up & exit room", "loc_bedroom", "08:00 AM", "Starts day"),
        ("rt_2", "user_01", 2, "Walk to Kitchen", "loc_kitchen", "08:15 AM", "Enters kitchen"),
        ("rt_3", "user_01", 3, "Medicine Interaction", "loc_kitchen", "08:20 AM", "Interacts with medicine container"),
        ("rt_4", "user_01", 4, "Breakfast at Dining Table", "loc_dining", "08:30 AM", "Eats morning meal"),
        ("rt_5", "user_01", 5, "Rest & Reading in Living Room", "loc_living_room", "08:50 AM", "Settles into living room chair")
    ]
    cursor.executemany(
        "INSERT INTO routines (id, user_id, step_order, activity, location_id, typical_time, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        baseline_routines
    )

    # Seed an initial initial verified history for morning anchor demo
    initial_events = [
        (
            "evt_seed_1", "user_01", "obj_person", "entered", "loc_bedroom",
            "2026-10-08T08:00:00", "8:00 AM", 0.98, "VERIFIED", "ZONE_MASKED",
            "Resident woke up and exited bedroom", '{"zone": "private"}'
        ),
        (
            "evt_seed_2", "user_01", "obj_person", "entered", "loc_kitchen",
            "2026-10-08T08:15:00", "8:15 AM", 0.96, "VERIFIED", "PUBLIC",
            "Resident entered kitchen area", '{"zone": "activity"}'
        ),
        (
            "evt_seed_3", "user_01", "obj_medicine", "interacted_with", "loc_kitchen",
            "2026-10-08T09:00:00", "9:00 AM", 0.95, "VERIFIED", "PUBLIC",
            "Morning medicine container interaction recorded in kitchen", '{"note": "interaction recorded, consumption not claimed"}'
        ),
        (
            "evt_seed_4", "user_01", "obj_glasses", "placed_on", "loc_living_room",
            "2026-10-08T08:55:00", "8:55 AM", 0.94, "VERIFIED", "PUBLIC",
            "Reading glasses observed resting on living-room coffee table", '{"surface": "coffee table"}'
        )
    ]
    cursor.executemany(
        "INSERT INTO events (id, user_id, object_id, action, location_id, timestamp, display_time, confidence, verification_status, privacy_status, description, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        initial_events
    )

    conn.commit()
    conn.close()

def reset_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS events")
    cursor.execute("DROP TABLE IF EXISTS routines")
    cursor.execute("DROP TABLE IF EXISTS objects")
    cursor.execute("DROP TABLE IF EXISTS locations")
    cursor.execute("DROP TABLE IF EXISTS users")
    conn.commit()
    conn.close()
    init_db()
    seed_db()
