"""Authentication service for SasthoSetu (Prompt 09 & Prompt 16).

Backs user login and registration with SQLite storage, SHA-256 password hashing,
centralized validators, privacy-conscious error messages, and activity logging.
"""

from typing import Any, Dict, Optional, Tuple
from database import db
from utils.logger import get_logger
from utils.validators import (
    validate_name,
    validate_password,
    validate_password_match,
    validate_username,
)

log = get_logger("auth")


def authenticate(
    username_or_email: str, password: str, db_path: Optional[str] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Validates login credentials against SQLite users table.

    Returns:
        (is_success, message, user_data_or_None)
    """
    clean_username = str(username_or_email).strip() if username_or_email else ""
    clean_password = str(password).strip() if password else ""

    # 1. Validation checks
    is_valid_user, user_err = validate_username(clean_username)
    if not is_valid_user:
        return False, user_err, None

    is_valid_pass, pass_err = validate_password(clean_password)
    if not is_valid_pass:
        return False, pass_err, None

    # 2. Query SQLite users table
    try:
        user_record = db.get_user_by_username(clean_username, db_path=db_path or db.DB_PATH)
    except Exception as err:
        log.error(f"Database error during authentication: {err}")
        return False, "A database error occurred. Please try again.", None

    # Privacy-conscious generic error: never reveal whether username or password was the cause
    if not user_record or not db.verify_password(clean_password, user_record["password_hash"]):
        log.warning(f"Failed login attempt for username: {clean_username}")
        return False, "Invalid username or password.", None

    # 3. Successful login (format dictionary for session)
    log.info(f"Successful login for user '{clean_username}' (Role: {user_record['role']})")
    session_user = {
        "id": user_record["id"],
        "full_name": user_record["full_name"],
        "username_or_email": user_record["username"],
        "role": user_record["role"],
    }
    return True, "Login successful.", session_user


def register(
    full_name: str,
    username_or_email: str,
    password: str,
    confirm_password: str,
    role: str = "patient_health_worker",
    db_path: Optional[str] = None,
) -> Tuple[bool, str]:
    """Validates and registers a new user in SQLite.

    Returns:
        (is_success, message)
    """
    clean_name = str(full_name).strip() if full_name else ""
    clean_username = str(username_or_email).strip() if username_or_email else ""
    clean_password = str(password).strip() if password else ""
    clean_confirm = str(confirm_password).strip() if confirm_password else ""

    # 1. Client-side centralized validation checks
    is_valid_name, name_err = validate_name(clean_name)
    if not is_valid_name:
        return False, name_err

    is_valid_user, user_err = validate_username(clean_username)
    if not is_valid_user:
        return False, user_err

    is_valid_pass, pass_err = validate_password(clean_password)
    if not is_valid_pass:
        return False, pass_err

    is_valid_match, match_err = validate_password_match(clean_password, clean_confirm)
    if not is_valid_match:
        return False, match_err

    # 2. Insert into SQLite users table
    try:
        success, msg, _ = db.create_user(
            full_name=clean_name,
            username=clean_username,
            password=clean_password,
            role=role,
            db_path=db_path or db.DB_PATH,
        )
        if not success:
            return False, msg

        log.info(f"New user registered successfully: '{clean_username}'")
        return True, "Account created successfully! You can now log in."
    except Exception as err:
        log.error(f"Error during registration: {err}")
        return False, "A database error occurred during registration. Please try again."
