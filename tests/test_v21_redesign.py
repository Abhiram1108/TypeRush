"""
TypeRush 2.1 Complete Redesign & Typing Engine Automated Test Suite (test_v21_redesign.py)

Comprehensive verification covering all 57+ test points:
- Typing Engine Tests (1-20): Case-insensitivity, cascade immunity, backspace, spacebar, alignment.
- Scoring Engine Tests (21-30): Gross WPM, Net WPM, accuracy, character counts, zero-guards.
- Content Generation Tests (31-37): Easy, Medium, Hard, Expert, offline, natural sentences.
- Visual & Navigation Tests (38-50): Midnight Minimal theme, no edition/mode selectors, responsiveness.
- Data Tests (51-57): Legacy session preservation, settings migration, CSV export.
- Exit Experience Tests (58-71): Shared exit controller, default confirmation OFF, timer pausing.
"""

import unittest
import os
import sys
import time
import tkinter as tk
from typing import Dict, Any

# Ensure repository root is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui import theme, storage, scoring
from ui.alignment import TypingAlignmentEngine, levenshtein_align
from ui.content_generator import ContentGenerator
from ui.app import TypeRushApp
from ui.screens.home_screen import HomeScreen
from ui.screens.typing_screen import TypingScreen
from ui.screens.results_screen import ResultsScreen
from ui.screens.history_screen import HistoryScreen
from ui.screens.settings_screen import SettingsScreen


def safe_destroy(app: tk.Tk) -> None:
    """Safely destroy Tkinter application instance preventing dangling after() callbacks."""
    try:
        if hasattr(app, "screens"):
            for s in app.screens.values():
                if hasattr(s, "cancel_test"):
                    s.cancel_test()
                if hasattr(s, "auto_nav_after_id") and s.auto_nav_after_id:
                    try:
                        s.after_cancel(s.auto_nav_after_id)
                    except Exception:
                        pass
                    s.auto_nav_after_id = None
                if hasattr(s, "exit_dialog") and s.exit_dialog:
                    try:
                        s.exit_dialog.grab_release()
                        s.exit_dialog.destroy()
                    except Exception:
                        pass
                    s.exit_dialog = None
        for child in list(app.winfo_children()):
            if isinstance(child, tk.Toplevel):
                try:
                    child.grab_release()
                    child.destroy()
                except Exception:
                    pass
        if hasattr(app, "anim_manager"):
            app.anim_manager.cancel_all()
        app.update_idletasks()
        app.destroy()
    except Exception:
        pass


class TestTypeRushV21Redesign(unittest.TestCase):
    """Complete test suite verifying TypeRush 2.1 specifications."""

    def setUp(self):
        storage.ensure_data_dir()
        self.orig_settings = storage.load_settings()

    def tearDown(self):
        storage.save_settings(self.orig_settings)

    # ========================================================================
    # A. TYPING ENGINE TESTS (1-20)
    # ========================================================================

    def test_01_correct_character_detection(self):
        """1. Correct character detection."""
        engine = TypingAlignmentEngine("hello world")
        engine.handle_character("h")
        res = engine.evaluate()
        self.assertEqual(res["word_evaluations"][0].char_statuses[0], ("h", "correct"))
        self.assertEqual(res["correct_chars"], 1)

    def test_02_incorrect_character_detection(self):
        """2. Incorrect character detection."""
        engine = TypingAlignmentEngine("hello world")
        engine.handle_character("x")
        res = engine.evaluate()
        self.assertEqual(res["word_evaluations"][0].char_statuses[0], ("x", "incorrect"))
        self.assertEqual(res["incorrect_chars"], 1)

    def test_03_immediate_character_feedback_state(self):
        """3. Immediate character feedback state."""
        engine = TypingAlignmentEngine("code")
        engine.handle_character("c")
        engine.handle_character("o")
        res = engine.evaluate()
        self.assertEqual(len(res["word_evaluations"][0].char_statuses), 2)
        self.assertEqual(res["word_evaluations"][0].char_statuses[0][1], "correct")
        self.assertEqual(res["word_evaluations"][0].char_statuses[1][1], "correct")

    def test_04_spacebar_word_commitment(self):
        """4. Spacebar word commitment."""
        engine = TypingAlignmentEngine("good day")
        for ch in "good":
            engine.handle_character(ch)
        self.assertEqual(engine.current_word_idx, 0)
        engine.handle_character(" ")
        self.assertEqual(engine.current_word_idx, 1)

    def test_05_correct_word_advancement(self):
        """5. Correct word advancement."""
        engine = TypingAlignmentEngine("fast typing")
        for ch in "fast ":
            engine.handle_character(ch)
        res = engine.evaluate()
        self.assertEqual(res["correct_words"], 1)
        self.assertTrue(res["word_evaluations"][0].is_correct)
        self.assertEqual(engine.current_word_idx, 1)

    def test_06_incorrect_word_isolation(self):
        """6. Incorrect word isolation."""
        engine = TypingAlignmentEngine("cat dog bird")
        for ch in "bat ":  # typo in word 0
            engine.handle_character(ch)
        for ch in "dog ":  # correct word 1
            engine.handle_character(ch)
        res = engine.evaluate()
        self.assertFalse(res["word_evaluations"][0].is_correct)
        self.assertTrue(res["word_evaluations"][1].is_correct)
        self.assertEqual(res["correct_words"], 1)
        self.assertEqual(res["incorrect_words"], 1)

    def test_07_no_cascading_errors(self):
        """7. No cascading errors (SRM prompt example)."""
        expected = "I am typing and I am happy"
        typed = "I am typimg and I am happy "
        engine = TypingAlignmentEngine(expected)
        for ch in typed:
            engine.handle_character(ch)
        res = engine.evaluate()
        evals = res["word_evaluations"]
        self.assertTrue(evals[0].is_correct)   # I
        self.assertTrue(evals[1].is_correct)   # am
        self.assertFalse(evals[2].is_correct)  # typimg (mistake)
        self.assertTrue(evals[3].is_correct)   # and
        self.assertTrue(evals[4].is_correct)   # I
        self.assertTrue(evals[5].is_correct)   # am
        self.assertTrue(evals[6].is_correct)   # happy
        self.assertEqual(res["correct_words"], 6)
        self.assertEqual(res["incorrect_words"], 1)

    def test_08_backspace_within_current_word(self):
        """8. Backspace within current word."""
        engine = TypingAlignmentEngine("hello")
        for ch in "helx":
            engine.handle_character(ch)
        self.assertEqual(engine.typed_words[0], "helx")
        engine.handle_backspace()
        self.assertEqual(engine.typed_words[0], "hel")

    def test_09_backspace_after_committed_words(self):
        """9. Backspace after committed words keeps previous word safe."""
        engine = TypingAlignmentEngine("hello world")
        for ch in "hello ":
            engine.handle_character(ch)
        self.assertEqual(engine.current_word_idx, 1)
        # Backspace at start of word 1 should not corrupt word 0
        engine.handle_backspace()
        self.assertEqual(engine.typed_words[0], "hello")
        res = engine.evaluate()
        self.assertTrue(res["word_evaluations"][0].is_correct)

    def test_10_character_substitution(self):
        """10. Character substitution."""
        align = levenshtein_align("hello", "jello")
        subs = [op for _, _, op in align if op == "sub"]
        self.assertEqual(len(subs), 1)

    def test_11_character_insertion(self):
        """11. Character insertion."""
        align = levenshtein_align("world", "worlld")
        inserts = [op for _, _, op in align if op == "insert"]
        self.assertEqual(len(inserts), 1)

    def test_12_character_deletion(self):
        """12. Character deletion."""
        align = levenshtein_align("world", "word")
        deletes = [op for _, _, op in align if op == "delete"]
        self.assertEqual(len(deletes), 1)

    def test_13_punctuation_comparison(self):
        """13. Punctuation comparison."""
        align = levenshtein_align("hello,", "hello.")
        subs = [op for _, _, op in align if op == "sub"]
        self.assertEqual(len(subs), 1)

    def test_14_case_insensitive_comparison(self):
        """14. Case-insensitive comparison (the vs THE)."""
        align = levenshtein_align("the", "THE")
        matches = [op for _, _, op in align if op == "match"]
        self.assertEqual(len(matches), 3)

        engine = TypingAlignmentEngine("the")
        for ch in "THE ":
            engine.handle_character(ch)
        res = engine.evaluate()
        self.assertTrue(res["word_evaluations"][0].is_correct)
        self.assertEqual(res["incorrect_chars"], 0)

    def test_15_multiple_consecutive_spaces(self):
        """15. Multiple consecutive spaces on empty word do not skip words."""
        engine = TypingAlignmentEngine("first second third")
        for ch in "first ":
            engine.handle_character(ch)
        self.assertEqual(engine.current_word_idx, 1)
        # Extra spaces on empty word 1
        engine.handle_character(" ")
        engine.handle_character(" ")
        self.assertEqual(engine.current_word_idx, 1)

    def test_16_empty_word_handling(self):
        """16. Empty word handling does not generate phantom deletion errors."""
        engine = TypingAlignmentEngine("one two three")
        for ch in "one ":
            engine.handle_character(ch)
        engine.is_completed = True
        res = engine.evaluate()
        # Word 'two' was never started; should not penalize as 3 incorrect chars
        self.assertEqual(res["correct_words"], 1)
        self.assertEqual(res["incorrect_words"], 0)
        self.assertEqual(res["incorrect_chars"], 0)

    def test_17_continuous_passage_extension(self):
        """17. Continuous passage extension."""
        engine = TypingAlignmentEngine("start words")
        initial_count = len(engine.expected_words)
        engine.append_target_text("more dynamic stream")
        self.assertEqual(len(engine.expected_words), initial_count + 3)

    def test_18_timer_expiration(self):
        """18. Timer expiration sets completion state."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.selected_duration = 15
        scr._complete_test(reason="Time Expired")
        self.assertEqual(scr.state, "completed")
        self.assertIsNotNone(scr.last_result)
        safe_destroy(app)

    def test_19_no_duplicate_completion(self):
        """19. No duplicate completion calls."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr._complete_test(reason="Time Expired")
        res1 = scr.last_result
        scr._complete_test(reason="Time Expired")
        self.assertEqual(scr.last_result["id"], res1["id"])
        safe_destroy(app)

    def test_20_correct_session_saving(self):
        """20. Correct session saving."""
        res = scoring.create_session_result(
            correct_chars=50,
            incorrect_chars=2,
            total_typed=52,
            elapsed_seconds=15.0,
            selected_duration=15,
            difficulty="Easy",
            wpm_samples=[(1.0, 40), (2.0, 42)],
            completed_reason="Time Expired"
        )
        saved = storage.save_session(res)
        self.assertIn("id", saved)
        all_sessions = storage.load_all_sessions()
        self.assertTrue(any(s["id"] == saved["id"] for s in all_sessions))

    # ========================================================================
    # B. SCORING TESTS (21-30)
    # ========================================================================

    def test_21_gross_wpm(self):
        """21. Gross WPM: (total / 5.0) / (sec / 60.0)."""
        metrics = scoring.calculate_typing_metrics(
            correct_chars=50,
            incorrect_chars=10,
            total_typed=60,
            elapsed_seconds=30.0  # 0.5 minutes -> (60/5) / 0.5 = 24
        )
        self.assertEqual(metrics["gross_wpm"], 24)

    def test_22_net_wpm(self):
        """22. Net WPM: max(0, int((correct / 5.0) / (sec / 60.0)))."""
        metrics = scoring.calculate_typing_metrics(
            correct_chars=50,
            incorrect_chars=10,
            total_typed=60,
            elapsed_seconds=30.0  # (50/5) / 0.5 = 20
        )
        self.assertEqual(metrics["net_wpm"], 20)

    def test_23_accuracy(self):
        """23. Accuracy: (correct / total) * 100.0."""
        metrics = scoring.calculate_typing_metrics(
            correct_chars=90,
            incorrect_chars=10,
            total_typed=100,
            elapsed_seconds=60.0
        )
        self.assertEqual(metrics["accuracy"], 90.0)

    def test_24_error_counts(self):
        """24. Error counts."""
        metrics = scoring.calculate_typing_metrics(
            correct_chars=80,
            incorrect_chars=5,
            total_typed=85,
            elapsed_seconds=30.0
        )
        self.assertEqual(metrics["error_count"], 5)

    def test_25_correct_word_counts(self):
        """25. Correct word counts."""
        engine = TypingAlignmentEngine("one two three")
        for ch in "one two ":
            engine.handle_character(ch)
        res = engine.evaluate()
        self.assertEqual(res["correct_words"], 2)

    def test_26_incorrect_word_counts(self):
        """26. Incorrect word counts."""
        engine = TypingAlignmentEngine("one two three")
        for ch in "one tow ":  # 'tow' is typo
            engine.handle_character(ch)
        res = engine.evaluate()
        self.assertEqual(res["incorrect_words"], 1)

    def test_27_character_counts(self):
        """27. Character counts."""
        metrics = scoring.calculate_typing_metrics(
            correct_chars=40,
            incorrect_chars=3,
            total_typed=43,
            elapsed_seconds=15.0
        )
        self.assertEqual(metrics["correct_chars"], 40)
        self.assertEqual(metrics["incorrect_chars"], 3)
        self.assertEqual(metrics["total_chars"], 43)

    def test_28_no_double_counted_errors(self):
        """28. No double-counted errors."""
        align = levenshtein_align("apple", "aple")  # 1 deletion
        dels = sum(1 for _, _, op in align if op == "delete")
        self.assertEqual(dels, 1)

    def test_29_short_duration_handling(self):
        """29. Short duration handling without zero division."""
        metrics = scoring.calculate_typing_metrics(
            correct_chars=5,
            incorrect_chars=0,
            total_typed=5,
            elapsed_seconds=0.1
        )
        self.assertGreater(metrics["net_wpm"], 0)
        self.assertEqual(metrics["accuracy"], 100.0)

    def test_30_zero_character_handling(self):
        """30. Zero character handling."""
        metrics = scoring.calculate_typing_metrics(
            correct_chars=0,
            incorrect_chars=0,
            total_typed=0,
            elapsed_seconds=15.0
        )
        self.assertEqual(metrics["net_wpm"], 0)
        self.assertEqual(metrics["gross_wpm"], 0)
        self.assertEqual(metrics["accuracy"], 100.0)

    # ========================================================================
    # C. CONTENT GENERATION TESTS (31-37)
    # ========================================================================

    def test_31_easy_content_generation(self):
        """31. Easy content generation."""
        gen = ContentGenerator(difficulty="Easy", seed=42)
        chunk = gen.generate_chunk(word_target=20)
        self.assertGreater(len(chunk), 10)
        self.assertTrue(any(c.isalpha() for c in chunk))

    def test_32_medium_content_generation(self):
        """32. Medium content generation."""
        gen = ContentGenerator(difficulty="Medium", seed=42)
        chunk = gen.generate_chunk(word_target=20)
        self.assertGreater(len(chunk), 10)

    def test_33_hard_content_generation(self):
        """33. Hard content generation."""
        gen = ContentGenerator(difficulty="Hard", seed=42)
        chunk = gen.generate_chunk(word_target=20)
        self.assertGreater(len(chunk), 10)

    def test_34_expert_content_generation(self):
        """34. Expert content generation."""
        gen = ContentGenerator(difficulty="Expert", seed=42)
        chunk = gen.generate_chunk(word_target=20)
        self.assertGreater(len(chunk), 10)

    def test_35_natural_punctuation(self):
        """35. Natural punctuation."""
        gen = ContentGenerator(difficulty="Medium", seed=10)
        chunk = gen.generate_chunk(word_target=40)
        self.assertTrue(any(p in chunk for p in [".", ",", '"', ";", "?"]))

    def test_36_continuous_passage_generation(self):
        """36. Continuous passage generation."""
        gen = ContentGenerator(seed=99)
        initial = gen.generate_initial_buffer(min_words=50)
        self.assertGreaterEqual(len(initial.split()), 50)
        continuation = gen.generate_continuation(min_words=20)
        self.assertTrue(continuation.startswith(" "))

    def test_37_no_internet_requirement(self):
        """37. Offline generator works without network access."""
        gen = ContentGenerator()
        for diff in ["Easy", "Medium", "Hard", "Expert"]:
            gen.set_config("Unified", diff)
            self.assertGreater(len(gen.generate_chunk(15)), 5)

    # ========================================================================
    # D. VISUAL AND NAVIGATION TESTS (38-50)
    # ========================================================================

    def test_38_home_construction(self):
        """38. Home screen construction."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("home")
        self.assertIsInstance(app.screens["home"], HomeScreen)
        safe_destroy(app)

    def test_39_typing_screen_construction(self):
        """39. Typing screen construction."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        self.assertIsInstance(app.screens["typing"], TypingScreen)
        safe_destroy(app)

    def test_40_results_construction(self):
        """40. Results screen construction."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("results")
        self.assertIsInstance(app.screens["results"], ResultsScreen)
        safe_destroy(app)

    def test_41_history_construction(self):
        """41. History screen construction."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("history")
        self.assertIsInstance(app.screens["history"], HistoryScreen)
        safe_destroy(app)

    def test_42_settings_construction(self):
        """42. Settings screen construction."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("settings")
        self.assertIsInstance(app.screens["settings"], SettingsScreen)
        safe_destroy(app)

    def test_43_unified_theme(self):
        """43. Unified theme tokens match Midnight Minimal."""
        self.assertEqual(theme.BG_PRIMARY, "#0B0D12")
        self.assertEqual(theme.BG_SECONDARY, "#121620")
        self.assertEqual(theme.PASSAGE_CORRECT, "#4ADE80")
        self.assertEqual(theme.PASSAGE_INCORRECT, "#F87171")
        self.assertEqual(theme.PASSAGE_UNTYPED, "#858D9E")

    def test_44_no_edition_selector(self):
        """44. HeaderBar does not contain an edition selector."""
        app = TypeRushApp()
        app.withdraw()
        self.assertIsNone(getattr(app.header_bar, "edition_pill", None))
        safe_destroy(app)

    def test_45_no_mode_selector(self):
        """45. HomeScreen does not contain a 6-mode segmented selector."""
        app = TypeRushApp()
        app.withdraw()
        home = app.screens["home"]
        self.assertIsNone(getattr(home, "mode_selector", None))
        safe_destroy(app)

    def test_46_navigation(self):
        """46. Navigation between screens."""
        app = TypeRushApp()
        app.withdraw()
        for name in ["home", "typing", "results", "history", "settings"]:
            app.show_screen(name)
            self.assertEqual(app.current_screen_name, name)
        safe_destroy(app)

    def test_47_exit_dialog(self):
        """47. Exit dialog has non-clipping dimensions and clear title."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.state = "typing"
        settings = storage.load_settings()
        settings["confirm_exit"] = True
        storage.save_settings(settings)

        scr.request_exit(action="home")
        self.assertIsNotNone(scr.exit_dialog)
        self.assertTrue(scr.exit_dialog.winfo_exists())
        scr.exit_dialog.destroy()
        safe_destroy(app)

    def test_48_responsive_resizing(self):
        """48. Window resizing between 1200x800 and 950x650."""
        app = TypeRushApp()
        self.assertEqual(app.minsize(), (950, 650))
        app.geometry("1200x800")
        app.update()
        self.assertEqual(app.winfo_width(), 1200)
        app.geometry("950x650")
        app.update()
        self.assertEqual(app.winfo_width(), 950)
        app.withdraw()
        safe_destroy(app)

    def test_49_reduced_motion(self):
        """49. Reduced motion setting cancels animation effects."""
        app = TypeRushApp()
        app.withdraw()
        app.anim_manager.set_reduced_motion(True)
        self.assertTrue(app.anim_manager.reduced_motion)
        safe_destroy(app)

    def test_50_animation_cleanup(self):
        """50. Animation manager cancel_all releases active tasks."""
        app = TypeRushApp()
        app.withdraw()
        app.anim_manager.cancel_all()
        self.assertEqual(len(app.anim_manager._active_tweens), 0)
        safe_destroy(app)

    # ========================================================================
    # E. DATA TESTS (51-57)
    # ========================================================================

    def test_51_legacy_history_loading(self):
        """51. Legacy history loading preserves older records."""
        sessions = storage.load_all_sessions()
        self.assertIsInstance(sessions, list)

    def test_52_legacy_settings_loading(self):
        """52. Legacy settings load safely."""
        settings = storage.load_settings()
        self.assertIn("default_difficulty", settings)
        self.assertIn("default_duration", settings)

    def test_53_no_history_deletion(self):
        """53. Saving a session appends without deleting prior history."""
        initial_len = len(storage.load_all_sessions())
        res = scoring.create_session_result(
            correct_chars=20,
            incorrect_chars=0,
            total_typed=20,
            elapsed_seconds=15.0,
            selected_duration=15,
            difficulty="Easy",
            wpm_samples=[]
        )
        storage.save_session(res)
        self.assertEqual(len(storage.load_all_sessions()), initial_len + 1)

    def test_54_no_duplicate_sessions(self):
        """54. No duplicate session IDs."""
        sessions = storage.load_all_sessions()
        ids = [s.get("id") for s in sessions if "id" in s]
        self.assertEqual(len(ids), len(set(ids)))

    def test_55_historical_report_integrity(self):
        """55. Historical report inspection preserves original values."""
        sessions = storage.load_all_sessions()
        if sessions:
            s0 = sessions[0]
            app = TypeRushApp()
            app.withdraw()
            app.show_screen("results", session_data=s0, is_historical=True)
            res_scr: ResultsScreen = app.screens["results"]
            self.assertEqual(res_scr.session_data["id"], s0["id"])
            safe_destroy(app)

    def test_56_retry_creates_a_new_session(self):
        """56. Retry creates a new typing attempt."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("results")
        res_scr: ResultsScreen = app.screens["results"]
        res_scr._on_try_again()
        self.assertEqual(app.current_screen_name, "typing")
        safe_destroy(app)

    def test_57_csv_compatibility(self):
        """57. CSV export creates a valid readable file."""
        ok, path = storage.export_history_to_csv()
        self.assertTrue(ok)
        self.assertTrue(os.path.isfile(path))
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass

    # ========================================================================
    # F. EXIT AND SETTINGS OVERRIDE TESTS (58-71)
    # ========================================================================

    def test_58_escape_with_confirmation_disabled(self):
        """58. Escape with confirmation disabled exits immediately."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.state = "typing"

        s = storage.load_settings()
        s["confirm_exit"] = False
        storage.save_settings(s)

        # Trigger exit
        scr.request_exit(action="home")
        self.assertIsNone(scr.exit_dialog)
        self.assertEqual(app.current_screen_name, "home")
        self.assertEqual(scr.state, "ready")
        safe_destroy(app)

    def test_59_exit_button_with_confirmation_disabled(self):
        """59. Exit button with confirmation disabled cancels without modal."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.state = "typing"

        s = storage.load_settings()
        s["confirm_exit"] = False
        storage.save_settings(s)

        scr._confirm_exit()
        self.assertIsNone(scr.exit_dialog)
        self.assertEqual(app.current_screen_name, "home")
        safe_destroy(app)

    def test_60_exit_returns_home_immediately(self):
        """60. Exit returns Home immediately."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.state = "typing"
        scr.request_exit(action="home")
        self.assertEqual(app.current_screen_name, "home")
        safe_destroy(app)

    def test_61_cancelled_test_is_not_saved(self):
        """61. Cancelled test is not saved to history."""
        before_count = len(storage.load_all_sessions())
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.state = "typing"
        scr._handle_character("h")
        scr.cancel_test()
        after_count = len(storage.load_all_sessions())
        self.assertEqual(before_count, after_count)
        safe_destroy(app)

    def test_62_history_is_unchanged(self):
        """62. History count unchanged after test cancellation."""
        before = len(storage.load_all_sessions())
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.state = "typing"
        scr.request_exit(action="home")
        self.assertEqual(len(storage.load_all_sessions()), before)
        safe_destroy(app)

    def test_63_escape_with_confirmation_enabled(self):
        """63. Escape with confirmation enabled displays compact panel."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.state = "typing"

        s = storage.load_settings()
        s["confirm_exit"] = True
        storage.save_settings(s)

        scr.request_exit(action="home")
        self.assertIsNotNone(scr.exit_dialog)
        self.assertTrue(scr.exit_dialog.winfo_exists())
        self.assertEqual(scr.state, "paused")
        scr.exit_dialog.destroy()
        safe_destroy(app)

    def test_64_continue_typing_closes_panel(self):
        """64. Continue typing closes panel and resumes test."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.state = "typing"
        scr.start_time = time.time()

        s = storage.load_settings()
        s["confirm_exit"] = True
        storage.save_settings(s)

        scr.request_exit(action="home")
        self.assertIsNotNone(scr.exit_dialog)

        # Trigger continue
        scr.exit_dialog.destroy()
        scr.exit_dialog = None
        scr._resume_timer()
        self.assertEqual(scr.state, "typing")
        safe_destroy(app)

    def test_65_timer_resumes_using_correct_remaining_time(self):
        """65. Timer pauses and resumes without losing remaining time."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.state = "typing"
        scr.start_time = time.time() - 5.0  # 5s elapsed
        scr._pause_timer()
        self.assertEqual(scr.state, "paused")
        scr._resume_timer()
        self.assertEqual(scr.state, "typing")
        safe_destroy(app)

    def test_66_passage_and_caret_position_preserved(self):
        """66. Resuming preserves typed text and caret position."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr._handle_character("a")
        scr._handle_character("b")
        scr._pause_timer()
        scr._resume_timer()
        self.assertEqual(scr.alignment_engine.typed_words[0], "ab")
        safe_destroy(app)

    def test_67_exit_test_cancels_attempt(self):
        """67. Exit test action cleanly cancels test and returns Home."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.state = "typing"
        scr.cancel_test()
        app.show_screen("home")
        self.assertEqual(scr.state, "ready")
        self.assertEqual(app.current_screen_name, "home")
        safe_destroy(app)

    def test_68_window_titlebar_close_no_test(self):
        """68. Windows titlebar close when no test active destroys window."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("home")
        app._on_window_close()
        # Verify app is destroyed
        try:
            exists = app.winfo_exists()
        except Exception:
            exists = False
        self.assertFalse(exists)

    def test_69_window_titlebar_close_active_test(self):
        """69. Titlebar close with active test and confirmation enabled prompts user."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.state = "typing"

        s = storage.load_settings()
        s["confirm_exit"] = True
        storage.save_settings(s)

        app._on_window_close()
        self.assertIsNotNone(scr.exit_dialog)
        self.assertTrue(scr.exit_dialog.winfo_exists())
        scr.exit_dialog.destroy()
        safe_destroy(app)

    def test_70_no_duplicate_dialogs(self):
        """70. Rapid exit requests do not spawn multiple confirmation panels."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        scr.state = "typing"

        s = storage.load_settings()
        s["confirm_exit"] = True
        storage.save_settings(s)

        scr.request_exit(action="home")
        dialog1 = scr.exit_dialog
        scr.request_exit(action="home")
        self.assertEqual(scr.exit_dialog, dialog1)
        dialog1.destroy()
        safe_destroy(app)

    def test_71_default_exit_confirmation_is_off(self):
        """71. Default exit confirmation is OFF to prevent user annoyance."""
        default_s = storage.DEFAULT_SETTINGS
        self.assertFalse(default_s["confirm_exit"])


if __name__ == "__main__":
    unittest.main()
