"""
TypeRush Local Storage & Persistence Layer

Provides persistent storage of completed typing sessions in `data/history.json`.
Features:
- Automatic directory creation and atomic writes
- Safe recovery from missing, empty, or corrupted JSON files
- Personal statistics computation (Personal Best, Average WPM, Average Accuracy, Total Tests)
- Duplicate save prevention via unique session UUIDs
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Base directory: project root / data / history.json
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# Default application preferences
DEFAULT_SETTINGS: Dict[str, Any] = {
    # Appearance
    "edition": "pleasant",
    "bg_intensity": "Balanced",
    "typing_contrast": "Standard",

    # Typing Experience
    "typing_feedback_mode": "live",
    "caret_style": "Highlight",
    "caret_blinking": True,
    "master_mode": False,  # Sudden Death mode: mistake terminates/resets test
    "passage_text_size": "medium",
    "passage_line_width": "balanced",
    "show_keyboard_hints": True,
    "show_live_metrics": True,

    # Audio Experience
    "sound_enabled": None,  # None = follow edition default (Soundscape: ON, Pleasant: OFF)
    "sound_volume": 70,
    "sound_keypress": True,
    "sound_ui_click": True,
    "sound_completion": True,
    "sound_error": False,

    # Accessibility & Animations
    "reduced_motion": False,
    "high_contrast": False,
    "show_tooltips": True,
    "interaction_feedback": True,

    # Practice Preferences
    "default_mode": "Mixed",
    "default_difficulty": "Medium",
    "default_duration": 60,
    "show_tips": True,
    "confirm_exit": False,
}


def get_storage_path() -> str:
    """Return absolute path to the history file."""
    return HISTORY_FILE


def get_settings_path() -> str:
    """Return absolute path to the settings file."""
    return SETTINGS_FILE


def ensure_data_dir() -> None:
    """Ensure that the data storage directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)


def load_all_sessions() -> List[Dict[str, Any]]:
    """
    Load all completed sessions from local storage, sorted by date descending (newest first).
    Handles missing, empty, or malformed JSON files gracefully without crashing.
    """
    ensure_data_dir()

    if not os.path.isfile(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)

        sessions = data.get("sessions", [])
        if not isinstance(sessions, list):
            return []

        # Sort newest first
        def parse_date(s):
            try:
                return datetime.fromisoformat(s.get("date", ""))
            except Exception:
                return datetime.min

        sessions.sort(key=parse_date, reverse=True)
        return sessions

    except (json.JSONDecodeError, ValueError) as err:
        # Corrupted JSON: preserve file by renaming to .corrupted.<timestamp>
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{HISTORY_FILE}.corrupted.{timestamp}"
            os.rename(HISTORY_FILE, backup_path)
        except Exception:
            pass
        return []
    except Exception:
        # File access/permission issue: return empty safely
        return []


def save_session(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save a completed typing session to local history.
    Assigns unique ID and timestamp if missing, prevents duplicate records,
    and performs safe atomic writes.
    """
    ensure_data_dir()

    # Create a copy so we don't mutate caller's object unexpectedly
    record = dict(session_data)

    # Ensure unique ID and timestamp
    if "id" not in record or not record["id"]:
        record["id"] = uuid.uuid4().hex[:12]

    if "date" not in record or not record["date"]:
        record["date"] = datetime.now().isoformat()

    # Load existing sessions
    existing_sessions = load_all_sessions()

    # Check for duplicate ID
    for existing in existing_sessions:
        if existing.get("id") == record["id"]:
            return existing

    # Prepend new session
    existing_sessions.insert(0, record)

    # Write atomically using a temporary file
    payload = {"sessions": existing_sessions}
    temp_file = f"{HISTORY_FILE}.tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        os.replace(temp_file, HISTORY_FILE)
    except Exception:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
        # Fallback direct write
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    return record


def save_all_sessions(sessions: List[Dict[str, Any]]) -> None:
    """
    Save an entire collection of completed sessions to local history.
    Useful for batch operations, imports, testing, and state restoration.
    """
    ensure_data_dir()
    payload = {"sessions": list(sessions)}
    temp_file = f"{HISTORY_FILE}.tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        os.replace(temp_file, HISTORY_FILE)
    except Exception:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


def get_latest_session() -> Optional[Dict[str, Any]]:
    """Return the most recently completed session or None."""
    sessions = load_all_sessions()
    return sessions[0] if sessions else None


def get_personal_best() -> int:
    """Return the maximum Net WPM recorded across saved sessions, or 0 if none."""
    sessions = load_all_sessions()
    if not sessions:
        return 0
    return max((s.get("net_wpm", 0) for s in sessions), default=0)


def get_average_wpm() -> int:
    """Return the arithmetic mean of Net WPM across all completed sessions."""
    sessions = load_all_sessions()
    if not sessions:
        return 0
    total = sum(s.get("net_wpm", 0) for s in sessions)
    return int(round(total / len(sessions)))


def get_average_accuracy() -> float:
    """Return the arithmetic mean accuracy percentage across all completed sessions."""
    sessions = load_all_sessions()
    if not sessions:
        return 0.0
    total = sum(float(s.get("accuracy", 0.0)) for s in sessions)
    return round(total / len(sessions), 1)


def get_total_tests() -> int:
    """Return total number of saved completed sessions."""
    sessions = load_all_sessions()
    return len(sessions)


def get_personal_statistics() -> Dict[str, Any]:
    """
    Compile comprehensive aggregate personal statistics from all saved sessions.
    """
    sessions = load_all_sessions()
    count = len(sessions)

    if count == 0:
        return {
            "total_tests": 0,
            "personal_best": 0,
            "average_wpm": 0,
            "average_accuracy": 0.0,
            "latest_session": None,
        }

    best_wpm = max((s.get("net_wpm", 0) for s in sessions), default=0)
    avg_wpm = int(round(sum(s.get("net_wpm", 0) for s in sessions) / count))
    avg_acc = round(sum(float(s.get("accuracy", 0.0)) for s in sessions) / count, 1)

    return {
        "total_tests": count,
        "personal_best": best_wpm,
        "average_wpm": avg_wpm,
        "average_accuracy": avg_acc,
        "latest_session": sessions[0],
    }


def clear_all_history() -> bool:
    """
    Clear all saved sessions by truncating `history.json` to an empty sessions array.
    Returns True on success, False on failure.
    """
    ensure_data_dir()
    try:
        payload = {"sessions": []}
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return True
    except Exception:
        return False


def delete_session(session_id: str) -> bool:
    """
    Delete a single session by its unique ID from local history.
    Performs atomic write and returns True if found and deleted, False otherwise.
    """
    ensure_data_dir()
    sessions = load_all_sessions()
    initial_len = len(sessions)
    filtered = [s for s in sessions if s.get("id") != session_id]

    if len(filtered) == initial_len:
        return False

    save_all_sessions(filtered)
    return True


def get_mode_statistics(sessions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
    """
    Calculate performance statistics partitioned across the 6 typing modes.
    Returns dictionary mapping mode name to:
    { "count": int, "avg_wpm": int, "best_wpm": int, "avg_accuracy": float }
    """
    if sessions is None:
        sessions = load_all_sessions()

    modes = ["Words", "Punctuation", "Capitalization", "Numbers", "Mixed", "Code"]
    stats = {}

    for mode in modes:
        if mode == "Numbers":
            matching = [s for s in sessions if s.get("mode") in ("Numbers", "Numbers & Symbols")]
        else:
            matching = [s for s in sessions if s.get("mode") == mode]

        cnt = len(matching)
        if cnt == 0:
            stats[mode] = {
                "count": 0,
                "avg_wpm": 0,
                "best_wpm": 0,
                "avg_accuracy": 0.0,
            }
        else:
            avg_w = int(round(sum(s.get("net_wpm", 0) for s in matching) / cnt))
            best_w = max((s.get("net_wpm", 0) for s in matching), default=0)
            avg_a = round(sum(float(s.get("accuracy", 0.0)) for s in matching) / cnt, 1)
            stats[mode] = {
                "count": cnt,
                "avg_wpm": avg_w,
                "best_wpm": best_w,
                "avg_accuracy": avg_a,
            }

    return stats


def get_difficulty_statistics(sessions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Dict[str, Any]]:
    """
    Calculate performance statistics partitioned across the 4 difficulty tiers.
    Returns dictionary mapping difficulty name to:
    { "count": int, "avg_wpm": int, "avg_accuracy": float }
    """
    if sessions is None:
        sessions = load_all_sessions()

    difficulties = ["Easy", "Medium", "Hard", "Expert"]
    stats = {}

    for diff in difficulties:
        matching = [s for s in sessions if s.get("difficulty") == diff]
        cnt = len(matching)
        if cnt == 0:
            stats[diff] = {
                "count": 0,
                "avg_wpm": 0,
                "avg_accuracy": 0.0,
            }
        else:
            avg_w = int(round(sum(s.get("net_wpm", 0) for s in matching) / cnt))
            avg_a = round(sum(float(s.get("accuracy", 0.0)) for s in matching) / cnt, 1)
            stats[diff] = {
                "count": cnt,
                "avg_wpm": avg_w,
                "avg_accuracy": avg_a,
            }

    return stats


def get_personal_records(sessions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Compile personal milestone records supported by genuine history.
    """
    if sessions is None:
        sessions = load_all_sessions()

    if not sessions:
        return {
            "best_wpm": 0,
            "best_wpm_session": None,
            "best_accuracy": 0.0,
            "best_accuracy_session": None,
            "best_words_wpm": 0,
            "best_words_session": None,
            "best_code_wpm": 0,
            "best_code_session": None,
            "most_practiced_mode": "None",
            "most_practiced_count": 0,
            "longest_session_seconds": 0,
            "longest_session": None,
            "most_recent_session": None,
        }

    # Best overall WPM
    best_wpm_sess = max(sessions, key=lambda s: s.get("net_wpm", 0), default=None)
    best_wpm = best_wpm_sess.get("net_wpm", 0) if best_wpm_sess else 0

    # Best accuracy (minimum 10 chars typed or net_wpm > 0)
    valid_acc = [s for s in sessions if s.get("total_chars", 0) >= 10 or s.get("net_wpm", 0) > 0]
    best_acc_sess = max(valid_acc if valid_acc else sessions, key=lambda s: float(s.get("accuracy", 0.0)), default=None)
    best_acc = float(best_acc_sess.get("accuracy", 0.0)) if best_acc_sess else 0.0

    # Best Words mode
    words_sessions = [s for s in sessions if s.get("mode") == "Words"]
    best_words_sess = max(words_sessions, key=lambda s: s.get("net_wpm", 0), default=None) if words_sessions else None
    best_words_wpm = best_words_sess.get("net_wpm", 0) if best_words_sess else 0

    # Best Code mode
    code_sessions = [s for s in sessions if s.get("mode") == "Code"]
    best_code_sess = max(code_sessions, key=lambda s: s.get("net_wpm", 0), default=None) if code_sessions else None
    best_code_wpm = best_code_sess.get("net_wpm", 0) if best_code_sess else 0

    # Most practiced mode
    mode_counts = {}
    for s in sessions:
        m = s.get("mode", "Mixed")
        mode_counts[m] = mode_counts.get(m, 0) + 1
    most_practiced_mode, most_practiced_count = max(mode_counts.items(), key=lambda item: item[1]) if mode_counts else ("None", 0)

    # Longest completed session
    longest_sess = max(sessions, key=lambda s: float(s.get("elapsed_seconds", s.get("selected_duration", 0))), default=None)
    longest_dur = int(round(float(longest_sess.get("elapsed_seconds", longest_sess.get("selected_duration", 0))))) if longest_sess else 0

    # Most recent session
    most_recent = sessions[0] if sessions else None

    return {
        "best_wpm": best_wpm,
        "best_wpm_session": best_wpm_sess,
        "best_accuracy": best_acc,
        "best_accuracy_session": best_acc_sess,
        "best_words_wpm": best_words_wpm,
        "best_words_session": best_words_sess,
        "best_code_wpm": best_code_wpm,
        "best_code_session": best_code_sess,
        "most_practiced_mode": most_practiced_mode,
        "most_practiced_count": most_practiced_count,
        "longest_session_seconds": longest_dur,
        "longest_session": longest_sess,
        "most_recent_session": most_recent,
    }


def export_history_to_csv(filepath: Optional[str] = None, sessions: Optional[List[Dict[str, Any]]] = None) -> Tuple[bool, str]:
    """
    Export all completed sessions to a CSV file.
    Uses standard library csv module.
    Returns (True, filepath_or_success_message) or (False, error_message).
    """
    import csv

    if filepath is None:
        filepath = os.path.join(DATA_DIR, f"typerush_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    if sessions is None:
        sessions = load_all_sessions()

    if not sessions:
        return False, "No sessions available to export."

    headers = [
        "id",
        "date",
        "time",
        "net_wpm",
        "gross_wpm",
        "accuracy",
        "error_count",
        "mode",
        "difficulty",
        "selected_duration",
        "elapsed_seconds",
        "correct_words",
        "incorrect_words",
        "correct_chars",
        "incorrect_chars",
        "rating",
        "completed_reason"
    ]

    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for s in sessions:
                raw_date = s.get("date", "")
                date_part = raw_date
                time_part = ""
                try:
                    dt = datetime.fromisoformat(raw_date)
                    date_part = dt.strftime("%Y-%m-%d")
                    time_part = dt.strftime("%H:%M:%S")
                except Exception:
                    pass

                writer.writerow([
                    s.get("id", ""),
                    date_part,
                    time_part,
                    s.get("net_wpm", 0),
                    s.get("gross_wpm", 0),
                    s.get("accuracy", 100.0),
                    s.get("error_count", s.get("incorrect_chars", 0)),
                    s.get("mode", "Mixed"),
                    s.get("difficulty", "Medium"),
                    s.get("selected_duration", 60),
                    s.get("elapsed_seconds", 0.0),
                    s.get("correct_words", 0),
                    s.get("incorrect_words", 0),
                    s.get("correct_chars", 0),
                    s.get("incorrect_chars", 0),
                    s.get("rating", "Intermediate"),
                    s.get("completed_reason", "Time Expired")
                ])

        return True, filepath
    except Exception as exc:
        return False, str(exc)


def export_history_to_json(filepath: Optional[str] = None) -> Tuple[bool, str]:
    """
    Export complete user session history as a JSON backup file.
    Returns (True, filepath) on success or (False, error_message).
    """
    ensure_data_dir()
    records = load_all_sessions()
    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(DATA_DIR, f"typerush_backup_{timestamp}.json")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        return True, filepath
    except Exception as exc:
        return False, str(exc)


def import_history_from_json(filepath: str) -> Tuple[bool, int, str]:
    """
    Import session records from an external JSON backup file.
    Merges records without duplicate session IDs.
    Returns (success: bool, imported_count: int, message: str).
    """
    ensure_data_dir()
    if not os.path.isfile(filepath):
        return False, 0, f"File not found: {filepath}"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            imported = json.load(f)
        if not isinstance(imported, list):
            return False, 0, "Invalid JSON structure: expected a list of sessions"

        existing = load_all_sessions()
        existing_ids = {s.get("id") for s in existing if isinstance(s, dict) and s.get("id")}

        added = 0
        for item in imported:
            if isinstance(item, dict) and item.get("id"):
                if item.get("id") not in existing_ids:
                    existing.append(item)
                    existing_ids.add(item.get("id"))
                    added += 1

        if added > 0:
            atomic_write_json(HISTORY_FILE, existing)
        return True, added, f"Imported {added} session records successfully"
    except Exception as exc:
        return False, 0, str(exc)


def load_settings() -> Dict[str, Any]:
    """
    Load user preferences from `data/settings.json`.
    Returns dictionary merged with default settings for any missing keys.
    Handles missing or corrupted JSON files gracefully.
    """
    ensure_data_dir()

    settings = dict(DEFAULT_SETTINGS)

    if not os.path.isfile(SETTINGS_FILE):
        return settings

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                loaded = json.loads(content)
                if isinstance(loaded, dict):
                    settings.update(loaded)
    except Exception:
        # Corrupted or unreadable settings file: return defaults safely
        pass

    return settings


def save_settings(settings_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save user preferences to `data/settings.json` using atomic write.
    Merges with defaults to maintain schema integrity.
    """
    ensure_data_dir()

    merged = dict(DEFAULT_SETTINGS)
    merged.update(settings_data)

    temp_file = f"{SETTINGS_FILE}.tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        os.replace(temp_file, SETTINGS_FILE)
    except Exception:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    return merged


def reset_settings_to_defaults() -> Dict[str, Any]:
    """
    Reset user preferences to factory defaults in `data/settings.json`.
    CRITICAL: NEVER touches, resets, or deletes `data/history.json`.
    """
    defaults = dict(DEFAULT_SETTINGS)
    return save_settings(defaults)


def reset_settings() -> Dict[str, Any]:
    """
    Reset user preferences back to default settings.
    """
    return save_settings(DEFAULT_SETTINGS)

