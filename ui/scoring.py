"""
TypeRush Centralized Scoring & Metrics Engine

Provides standardized calculations for Net WPM, Gross WPM, Accuracy,
error counts, and skill ratings across the application without duplicated logic.
"""

from typing import Dict, Any, List, Tuple, Optional


def calculate_typing_metrics(
    correct_chars: int,
    incorrect_chars: int,
    total_typed: int,
    elapsed_seconds: float,
    weak_keys: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Compute standardized typing speed and precision metrics.

    Formulas:
    - Standard word length = 5 characters
    - Elapsed minutes = elapsed_seconds / 60.0
    - Gross WPM = (total_typed / 5.0) / elapsed_minutes
    - Net WPM = max(0, int((correct_chars / 5.0) / elapsed_minutes))
    - Accuracy = (correct_chars / total_typed) * 100.0 (if total_typed > 0 else 100.0)
    """
    safe_time = max(0.5, float(elapsed_seconds))
    minutes = safe_time / 60.0

    # Prevent division by zero and negative metrics
    total = max(0, int(total_typed))
    correct = max(0, int(correct_chars))
    errors = max(0, int(incorrect_chars))

    if total == 0 or float(elapsed_seconds) <= 0.0:
        accuracy = 100.0 if total == 0 else round((correct / total) * 100.0, 1)
        gross_wpm = 0
        net_wpm = 0
    else:
        accuracy = round((correct / total) * 100.0, 1)
        gross_wpm = int(round((total / 5.0) / minutes))
        net_wpm = max(0, int(round((correct / 5.0) / minutes)))

    return {
        "net_wpm": net_wpm,
        "gross_wpm": gross_wpm,
        "accuracy": accuracy,
        "error_count": errors,
        "correct_chars": correct,
        "incorrect_chars": errors,
        "total_chars": total,
        "elapsed_seconds": round(elapsed_seconds, 1),
        "weak_keys": dict(weak_keys or {}),
    }


def get_performance_rating(net_wpm: int) -> Tuple[str, str]:
    """
    Classify typing performance into descriptive skill levels with
    contextual descriptions.

    Levels:
    - < 30: Beginner
    - 30 - 49: Developing
    - 50 - 69: Intermediate
    - 70 - 89: Advanced
    - >= 90: Expert
    """
    if net_wpm < 30:
        return "Beginner", "Building keyboard familiarity and finger placement."
    elif net_wpm < 50:
        return "Developing", "Developing steady typing rhythm and muscle memory."
    elif net_wpm < 70:
        return "Intermediate", "Solid conversational typing pace with consistent accuracy."
    elif net_wpm < 90:
        return "Advanced", "High-velocity typing with exceptional fluency."
    else:
        return "Expert", "Professional-grade typing speed with master-level precision."


def calculate_consistency(wpm_samples: List[Tuple[float, int]]) -> Tuple[int, str, float, float]:
    """
    Calculate typing cadence consistency score from WPM sample history.

    Formula:
    - Mean (mu) = sum(wpm) / N
    - Standard Deviation (sigma) = sqrt(sum((wpm - mu)^2) / N)
    - Coefficient of Variation (CV) = sigma / mu
    - Consistency % = max(0, min(100, round(100.0 - (CV * 100.0))))

    Returns:
    - consistency_pct: int (0 to 100)
    - rating_label: str
    - std_dev: float
    - mean_wpm: float
    """
    if not wpm_samples or len(wpm_samples) < 2:
        val = float(wpm_samples[0][1]) if wpm_samples else 0.0
        return 100, "Baseline (Single sample)", 0.0, val

    w_vals = [float(s[1]) for s in wpm_samples]
    n = len(w_vals)
    mean_w = sum(w_vals) / n

    if mean_w <= 0.0:
        return 100, "Baseline (Zero speed)", 0.0, 0.0

    variance = sum((x - mean_w) ** 2 for x in w_vals) / n
    std_dev = variance ** 0.5
    cv = std_dev / mean_w
    consistency_pct = max(0, min(100, int(round(100.0 - (cv * 100.0)))))

    if consistency_pct >= 90:
        rating = "Exceptional Rhythm (Minimal fluctuation)"
    elif consistency_pct >= 80:
        rating = "High Stability (Steady pacing across intervals)"
    elif consistency_pct >= 65:
        rating = "Moderate Variation (Variable speed bursts)"
    else:
        rating = "Irregular Cadence (High variance between intervals)"

    return consistency_pct, rating, round(std_dev, 1), round(mean_w, 1)


def create_session_result(
    correct_chars: int,
    incorrect_chars: int,
    total_typed: int,
    elapsed_seconds: float,
    selected_duration: int,
    difficulty: str,
    wpm_samples: List[Tuple[float, int]],
    completed_reason: str = "Time Expired",
    mode: str = "Mixed",
    correct_words: int = 0,
    incorrect_words: int = 0,
    substitutions: int = 0,
    insertions: int = 0,
    omissions: int = 0,
    mistakes: Optional[List[Dict[str, Any]]] = None,
    consistency: Optional[int] = None,
    weak_keys: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """
    Assemble a comprehensive typing session summary dictionary.
    Supports continuous typing modes, word statistics, error categories,
    mistake review, and rhythm consistency.
    """
    metrics = calculate_typing_metrics(
        correct_chars=correct_chars,
        incorrect_chars=incorrect_chars,
        total_typed=total_typed,
        elapsed_seconds=elapsed_seconds,
        weak_keys=weak_keys
    )
    rating, rating_desc = get_performance_rating(metrics["net_wpm"])

    # Calculate consistency metrics if not explicitly passed
    if consistency is None:
        c_pct, c_rating, s_dev, m_wpm = calculate_consistency(wpm_samples)
    else:
        c_pct = consistency
        _, c_rating, s_dev, m_wpm = calculate_consistency(wpm_samples)

    return {
        **metrics,
        "rating": rating,
        "rating_desc": rating_desc,
        "selected_duration": selected_duration,
        "difficulty": difficulty,
        "mode": mode,
        "correct_words": correct_words,
        "incorrect_words": incorrect_words,
        "substitutions": substitutions,
        "insertions": insertions,
        "omissions": omissions,
        "mistakes": list(mistakes) if mistakes is not None else [],
        "consistency": c_pct,
        "consistency_rating": c_rating,
        "std_dev": s_dev,
        "mean_wpm": m_wpm,
        "wpm_samples": list(wpm_samples),
        "completed_reason": completed_reason,
    }
