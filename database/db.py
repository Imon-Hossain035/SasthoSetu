"""SQLite database manager for SasthoSetu (Prompt 09 & Prompt 16).

This module handles:
- Database connection management with foreign key enforcement.
- Schema initialization (users, patients, triage_records, audit_logs).
- Password hashing and verification.
- CRUD helper functions for all tables using parameterized queries.
- Robust SQLite error handling with rollbacks and centralized logging.
- Status transition validation (protecting completed consultations).
"""

import hashlib
import os
import sqlite3
import sys
from typing import Any, Dict, List, Optional, Tuple

from core import constants
from utils.logger import get_logger
from utils.validators import validate_clinician_notes, validate_status_transition

log = get_logger("db")


def get_app_base_dir() -> str:
    """Returns a reliable writable directory for persistent application data.

    When running as a packaged PyInstaller executable (sys.frozen=True),
    places user data in the directory containing the executable if writable,
    or falls back safely to %LOCALAPPDATA%\\SasthoSetu.
    When running in development, uses the project root directory.
    """
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        test_file = os.path.join(exe_dir, ".write_test")
        try:
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            return exe_dir
        except (PermissionError, OSError):
            app_data = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
            fallback_dir = os.path.join(app_data, "SasthoSetu")
            os.makedirs(fallback_dir, exist_ok=True)
            return fallback_dir
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Database file location in the project environment
BASE_DIR = get_app_base_dir()
DB_PATH = os.path.join(BASE_DIR, "sasthosetu.db")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Returns a SQLite connection with foreign keys enabled and row dictionary access."""
    target_path = db_path if db_path is not None else DB_PATH
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def hash_password(password: str) -> str:
    """Hashes a plain-text password using SHA-256 for secure local storage."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a stored SHA-256 hash."""
    return hash_password(plain_password) == hashed_password


def initialize_database(db_path: str = DB_PATH) -> None:
    """Creates the SQLite database schema if tables do not already exist.

    Safe to run repeatedly; preserves all existing records.
    """
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()

            # 1. Users Table (Authentication and role association)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'patient_health_worker',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # 2. Patients Table (Demographics and location)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    gender TEXT NOT NULL,
                    location TEXT NOT NULL,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # 3. Triage Records Table (Symptom reports, queue status, and triage outputs)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS triage_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
                    symptoms TEXT NOT NULL,
                    symptom_duration REAL,
                    duration_unit TEXT,
                    reported_severity TEXT,
                    additional_information TEXT,
                    urgency_level TEXT,
                    triage_reason TEXT,
                    triage_advice TEXT,
                    matched_rules TEXT,
                    triage_source TEXT,
                    clinician_override_urgency TEXT,
                    clinician_notes TEXT,
                    final_urgency TEXT,
                    reviewed_by TEXT,
                    reviewed_at TIMESTAMP,
                    status TEXT NOT NULL DEFAULT 'Waiting',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # Ensure schema migrations for existing database instances (Prompt 10, 12 & 15)
            cursor.execute("PRAGMA table_info(triage_records);")
            columns = [col[1] for col in cursor.fetchall()]
            if "matched_rules" not in columns:
                cursor.execute("ALTER TABLE triage_records ADD COLUMN matched_rules TEXT;")
            if "triage_source" not in columns:
                cursor.execute("ALTER TABLE triage_records ADD COLUMN triage_source TEXT;")
            if "clinician_override_urgency" not in columns:
                cursor.execute("ALTER TABLE triage_records ADD COLUMN clinician_override_urgency TEXT;")
            if "clinician_notes" not in columns:
                cursor.execute("ALTER TABLE triage_records ADD COLUMN clinician_notes TEXT;")
            if "final_urgency" not in columns:
                cursor.execute("ALTER TABLE triage_records ADD COLUMN final_urgency TEXT;")
            if "reviewed_by" not in columns:
                cursor.execute("ALTER TABLE triage_records ADD COLUMN reviewed_by TEXT;")
            if "reviewed_at" not in columns:
                cursor.execute("ALTER TABLE triage_records ADD COLUMN reviewed_at TIMESTAMP;")

            # 4. Audit Logs Table (Clinician review trail and status changes)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    triage_record_id INTEGER REFERENCES triage_records(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES users(id),
                    action TEXT NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # Seed pre-configured test users if users table is empty
            cursor.execute("SELECT COUNT(*) FROM users;")
            if cursor.fetchone()[0] == 0:
                seed_users = [
                    (
                        "Rahima Begum (Health Worker)",
                        "testuser",
                        hash_password("password123"),
                        "patient_health_worker",
                    ),
                    (
                        "Dr. Aminul Islam",
                        "demo@sasthosetu.org",
                        hash_password("password123"),
                        "clinician",
                    ),
                ]
                cursor.executemany(
                    """
                    INSERT INTO users (full_name, username, password_hash, role)
                    VALUES (?, ?, ?, ?);
                    """,
                    seed_users,
                )

            conn.commit()
            log.info("Database initialized successfully.")
    except sqlite3.Error as err:
        log.error(f"Failed to initialize database: {err}")
        raise


# =============================================================================
# User Operations
# =============================================================================

def create_user(
    full_name: str,
    username: str,
    password: str,
    role: str = "patient_health_worker",
    db_path: str = DB_PATH,
) -> Tuple[bool, str, Optional[int]]:
    """Creates a new user record with a hashed password."""
    clean_username = username.strip()
    hashed = hash_password(password.strip())

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (full_name, username, password_hash, role)
                VALUES (?, ?, ?, ?);
                """,
                (full_name.strip(), clean_username, hashed, role),
            )
            conn.commit()
            log.info(f"User account created: {clean_username} (Role: {role})")
            return True, "User created successfully.", cursor.lastrowid
    except sqlite3.IntegrityError:
        log.warning(f"Registration conflict: username '{clean_username}' already exists.")
        return False, "An account with this username or email already exists.", None
    except sqlite3.Error as err:
        log.error(f"Database error in create_user: {err}")
        return False, "A database error occurred while creating the account.", None


def get_user_by_username(
    username: str, db_path: str = DB_PATH
) -> Optional[Dict[str, Any]]:
    """Retrieves a user by username/email (case-insensitive)."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE LOWER(username) = LOWER(?);",
                (username.strip(),),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as err:
        log.error(f"Database error in get_user_by_username: {err}")
        return None


# =============================================================================
# Patient Operations
# =============================================================================

def create_patient(
    name: str,
    age: int,
    gender: str,
    location: str,
    phone: Optional[str] = None,
    db_path: str = DB_PATH,
) -> int:
    """Inserts a new patient record and returns the generated patient_id."""
    clean_phone = phone.strip() if phone and phone.strip() != "N/A" else None

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO patients (name, age, gender, location, phone)
            VALUES (?, ?, ?, ?, ?);
            """,
            (name.strip(), int(age), gender.strip(), location.strip(), clean_phone),
        )
        conn.commit()
        last_id = cursor.lastrowid
        log.info(f"Created patient record ID {last_id}")
        return last_id
    except sqlite3.Error as err:
        conn.rollback()
        log.error(f"Database error in create_patient: {err}")
        raise
    finally:
        conn.close()


def get_patient_by_id(
    patient_id: int, db_path: str = DB_PATH
) -> Optional[Dict[str, Any]]:
    """Retrieves a patient record by ID."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients WHERE id = ?;", (patient_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as err:
        log.error(f"Database error in get_patient_by_id for ID {patient_id}: {err}")
        return None


# =============================================================================
# Triage Record Operations
# =============================================================================

def create_triage_record(
    patient_id: int,
    symptoms: str,
    symptom_duration: Optional[float] = None,
    duration_unit: Optional[str] = None,
    reported_severity: Optional[str] = None,
    additional_information: Optional[str] = None,
    urgency_level: Optional[str] = None,
    triage_reason: Optional[str] = None,
    triage_advice: Optional[str] = None,
    matched_rules: Optional[str] = None,
    triage_source: Optional[str] = None,
    status: str = "Waiting",
    db_path: str = DB_PATH,
) -> int:
    """Inserts an assessment into triage_records and returns the record ID."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO triage_records (
                patient_id, symptoms, symptom_duration, duration_unit,
                reported_severity, additional_information, urgency_level,
                triage_reason, triage_advice, matched_rules, triage_source, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                patient_id,
                symptoms.strip(),
                symptom_duration,
                duration_unit,
                reported_severity,
                additional_information,
                urgency_level,
                triage_reason,
                triage_advice,
                matched_rules,
                triage_source,
                status,
            ),
        )
        conn.commit()
        last_id = cursor.lastrowid
        log.info(f"Created triage assessment ID {last_id} for Patient {patient_id} (Urgency: {urgency_level})")
        return last_id
    except sqlite3.Error as err:
        conn.rollback()
        log.error(f"Database error in create_triage_record: {err}")
        raise
    finally:
        conn.close()


def get_triage_record_by_id(
    record_id: int, db_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Retrieves a triage record by ID, joined with patient demographics."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    tr.*,
                    p.name AS patient_name,
                    p.age AS patient_age,
                    p.gender AS patient_gender,
                    p.location AS patient_location,
                    p.phone AS patient_phone
                FROM triage_records tr
                JOIN patients p ON tr.patient_id = p.id
                WHERE tr.id = ?;
                """,
                (record_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as err:
        log.error(f"Database error in get_triage_record_by_id for ID {record_id}: {err}")
        return None


def get_all_triage_records(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all triage records ordered by priority queue rules (Prompt 14 & 15).

    Ordering:
    1. Consultation Status: Waiting (1) -> In Consultation (2) -> Completed / Other (3)
    2. Effective Urgency Priority: URGENT (1) -> PENDING (2) -> MODERATE (3) -> ROUTINE (4) -> OTHER (5)
    3. FIFO Arrival: created_at ASC (oldest arrival first within urgency tier)
    """
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    tr.*,
                    p.name AS patient_name,
                    p.age AS patient_age,
                    p.gender AS patient_gender,
                    p.location AS patient_location,
                    p.phone AS patient_phone
                FROM triage_records tr
                JOIN patients p ON tr.patient_id = p.id
                ORDER BY 
                    CASE 
                        WHEN tr.status = 'Waiting' THEN 1
                        WHEN tr.status = 'In Consultation' THEN 2
                        ELSE 3
                    END ASC,
                    CASE 
                        WHEN COALESCE(tr.final_urgency, tr.urgency_level) = 'URGENT' THEN 1
                        WHEN COALESCE(tr.final_urgency, tr.urgency_level) IS NULL 
                             OR COALESCE(tr.final_urgency, tr.urgency_level) = 'PENDING_CONTEXTUAL_TRIAGE' 
                             OR COALESCE(tr.final_urgency, tr.urgency_level) = 'PENDING' 
                             OR COALESCE(tr.final_urgency, tr.urgency_level) = '' THEN 2
                        WHEN COALESCE(tr.final_urgency, tr.urgency_level) = 'MODERATE' THEN 3
                        WHEN COALESCE(tr.final_urgency, tr.urgency_level) = 'ROUTINE' THEN 4
                        ELSE 5
                    END ASC,
                    tr.created_at ASC;
                """
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    except sqlite3.Error as err:
        log.error(f"Database error in get_all_triage_records: {err}")
        raise


def get_waiting_patients(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all patients currently in 'Waiting' status ordered by effective priority and FIFO (Prompt 15)."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    tr.*,
                    p.name AS patient_name,
                    p.age AS patient_age,
                    p.gender AS patient_gender,
                    p.location AS patient_location,
                    p.phone AS patient_phone
                FROM triage_records tr
                JOIN patients p ON tr.patient_id = p.id
                WHERE tr.status = 'Waiting'
                ORDER BY 
                    CASE 
                        WHEN COALESCE(tr.final_urgency, tr.urgency_level) = 'URGENT' THEN 1
                        WHEN COALESCE(tr.final_urgency, tr.urgency_level) IS NULL 
                             OR COALESCE(tr.final_urgency, tr.urgency_level) = 'PENDING_CONTEXTUAL_TRIAGE' 
                             OR COALESCE(tr.final_urgency, tr.urgency_level) = 'PENDING' 
                             OR COALESCE(tr.final_urgency, tr.urgency_level) = '' THEN 2
                        WHEN COALESCE(tr.final_urgency, tr.urgency_level) = 'MODERATE' THEN 3
                        WHEN COALESCE(tr.final_urgency, tr.urgency_level) = 'ROUTINE' THEN 4
                        ELSE 5
                    END ASC,
                    tr.created_at ASC;
                """
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    except sqlite3.Error as err:
        log.error(f"Database error in get_waiting_patients: {err}")
        raise


def get_priority_queue_records(
    status: Optional[str] = "Waiting", db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieves triage records ordered strictly by effective priority and arrival FIFO."""
    if status and status != "All Statuses":
        try:
            with get_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT 
                        tr.*,
                        p.name AS patient_name,
                        p.age AS patient_age,
                        p.gender AS patient_gender,
                        p.location AS patient_location,
                        p.phone AS patient_phone
                    FROM triage_records tr
                    JOIN patients p ON tr.patient_id = p.id
                    WHERE tr.status = ?
                    ORDER BY 
                        CASE 
                            WHEN COALESCE(tr.final_urgency, tr.urgency_level) = 'URGENT' THEN 1
                            WHEN COALESCE(tr.final_urgency, tr.urgency_level) IS NULL 
                                 OR COALESCE(tr.final_urgency, tr.urgency_level) = 'PENDING_CONTEXTUAL_TRIAGE' 
                                 OR COALESCE(tr.final_urgency, tr.urgency_level) = 'PENDING' 
                                 OR COALESCE(tr.final_urgency, tr.urgency_level) = '' THEN 2
                            WHEN COALESCE(tr.final_urgency, tr.urgency_level) = 'MODERATE' THEN 3
                            WHEN COALESCE(tr.final_urgency, tr.urgency_level) = 'ROUTINE' THEN 4
                            ELSE 5
                        END ASC,
                        tr.created_at ASC;
                    """,
                    (status,),
                )
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
        except sqlite3.Error as err:
            log.error(f"Database error in get_priority_queue_records: {err}")
            raise
    else:
        return get_all_triage_records(db_path=db_path)


def update_triage_record(
    record_id: int,
    db_path: Optional[str] = None,
    **kwargs: Any,
) -> bool:
    """Updates fields on an existing triage record safely."""
    if not kwargs:
        return False

    allowed_columns = {
        "symptoms",
        "symptom_duration",
        "duration_unit",
        "reported_severity",
        "urgency_level",
        "triage_reason",
        "triage_advice",
        "matched_rules",
        "triage_source",
        "clinician_override_urgency",
        "clinician_notes",
        "final_urgency",
        "reviewed_by",
        "reviewed_at",
        "status",
        "additional_information",
    }
    updates = []
    values = []

    for key, value in kwargs.items():
        if key in allowed_columns:
            updates.append(f"{key} = ?")
            values.append(value)

    if not updates:
        return False

    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(record_id)

    sql = f"UPDATE triage_records SET {', '.join(updates)} WHERE id = ?;"

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(values))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as err:
        conn.rollback()
        log.error(f"Database error in update_triage_record for record {record_id}: {err}")
        return False
    finally:
        conn.close()


def save_clinician_review(
    record_id: int,
    reviewed_by: str,
    clinician_notes: Optional[str] = None,
    clinician_override_urgency: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    db_path: Optional[str] = None,
) -> bool:
    """Saves a clinician review, calculating effective urgency and creating an audit log entry (Prompt 15 & 16).

    Enforces:
    - Protection against reopening completed consultations.
    - Note length validation (max 2000 chars).
    - Preservation of the original automated assessment for medical audit.
    """
    # 1. Notes length validation
    if clinician_notes:
        is_valid_notes, notes_err = validate_clinician_notes(clinician_notes)
        if not is_valid_notes:
            log.warning(f"Clinician review rejected for record {record_id}: {notes_err}")
            raise ValueError(notes_err)

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM triage_records WHERE id = ?;", (record_id,))
        row = cursor.fetchone()
        if not row:
            log.warning(f"Review target record {record_id} not found in database.")
            return False

        existing = dict(row)
        current_status = existing.get("status", constants.STATUS_WAITING)
        automated_urgency = existing.get("urgency_level")

        target_status = status if status else current_status

        # 2. Status transition validation: Prevent reopening Completed consultations
        is_valid_trans, trans_err = validate_status_transition(current_status, target_status)
        if not is_valid_trans:
            log.warning(f"Invalid status transition attempted on record {record_id}: {trans_err}")
            raise ValueError(trans_err)

        # 3. Determine effective / final urgency
        if (
            clinician_override_urgency
            and clinician_override_urgency != constants.OVERRIDE_USE_AUTOMATED
            and str(clinician_override_urgency).strip()
        ):
            final_urgency = clinician_override_urgency.strip()
            stored_override = final_urgency
        else:
            final_urgency = automated_urgency
            stored_override = None

        cursor.execute(
            """
            UPDATE triage_records
            SET clinician_override_urgency = ?,
                clinician_notes = ?,
                final_urgency = ?,
                reviewed_by = ?,
                reviewed_at = CURRENT_TIMESTAMP,
                status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (
                stored_override,
                clinician_notes.strip() if clinician_notes else None,
                final_urgency,
                reviewed_by.strip() if reviewed_by else "Clinician",
                target_status,
                record_id,
            ),
        )
        conn.commit()
        log.info(f"Clinician review saved for record {record_id}: Final Urgency={final_urgency}, Status={target_status}")
    except (sqlite3.Error, ValueError) as err:
        conn.rollback()
        if isinstance(err, sqlite3.Error):
            log.error(f"Database error in save_clinician_review for record {record_id}: {err}")
        raise
    finally:
        conn.close()

    # Create audit trail log
    details = (
        f"Clinician: {reviewed_by} | Automated: {automated_urgency} | "
        f"Override: {stored_override or 'None'} | Final Urgency: {final_urgency} | Status: {target_status}"
    )
    if clinician_notes:
        details += f" | Notes: {clinician_notes.strip()[:100]}"

    try:
        create_audit_log(
            triage_record_id=record_id,
            user_id=user_id,
            action="CLINICIAN_REVIEW",
            details=details,
            db_path=db_path or DB_PATH,
        )
    except Exception as audit_err:
        log.warning(f"Failed to record audit log for record {record_id}: {audit_err}")

    return True


def update_consultation_status(
    record_id: int,
    new_status: str,
    user_id: Optional[int] = None,
    reviewed_by: Optional[str] = None,
    db_path: Optional[str] = None,
) -> bool:
    """Updates a patient's consultation status and records the transition in audit logs (Prompt 15 & 16)."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM triage_records WHERE id = ?;", (record_id,))
        row = cursor.fetchone()
        if not row:
            return False

        current_status = row["status"]
        is_valid_trans, trans_err = validate_status_transition(current_status, new_status)
        if not is_valid_trans:
            log.warning(f"Blocked invalid status transition on record {record_id}: {trans_err}")
            raise ValueError(trans_err)

        cursor.execute(
            """
            UPDATE triage_records
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (new_status, record_id),
        )
        conn.commit()
        log.info(f"Status transition for record {record_id}: {current_status} -> {new_status}")
    except (sqlite3.Error, ValueError) as err:
        conn.rollback()
        if isinstance(err, sqlite3.Error):
            log.error(f"Database error in update_consultation_status for record {record_id}: {err}")
        raise
    finally:
        conn.close()

    try:
        create_audit_log(
            triage_record_id=record_id,
            user_id=user_id,
            action=f"STATUS_CHANGE_{new_status.upper().replace(' ', '_')}",
            details=f"Status updated to '{new_status}' by {reviewed_by or 'Clinician'}.",
            db_path=db_path or DB_PATH,
        )
    except Exception as audit_err:
        log.warning(f"Failed to record status change audit log for record {record_id}: {audit_err}")

    return True


# =============================================================================
# Audit Log Operations
# =============================================================================

def create_audit_log(
    triage_record_id: Optional[int],
    user_id: Optional[int],
    action: str,
    details: Optional[str] = None,
    db_path: str = DB_PATH,
) -> int:
    """Records a clinician or system audit event."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_logs (triage_record_id, user_id, action, details)
            VALUES (?, ?, ?, ?);
            """,
            (triage_record_id, user_id, action.strip(), details),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as err:
        conn.rollback()
        log.error(f"Database error in create_audit_log: {err}")
        raise
    finally:
        conn.close()


def get_audit_logs(
    triage_record_id: Optional[int] = None, db_path: str = DB_PATH
) -> List[Dict[str, Any]]:
    """Retrieves audit logs, optionally filtered by triage_record_id."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            if triage_record_id is not None:
                cursor.execute(
                    "SELECT * FROM audit_logs WHERE triage_record_id = ? ORDER BY created_at ASC;",
                    (triage_record_id,),
                )
            else:
                cursor.execute("SELECT * FROM audit_logs ORDER BY created_at ASC;")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    except sqlite3.Error as err:
        log.error(f"Database error in get_audit_logs: {err}")
        return []
