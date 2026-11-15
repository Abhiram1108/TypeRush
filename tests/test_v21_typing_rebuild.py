"""
TypeRush 2.1 — Critical Typing Experience Rebuild Test Suite (test_v21_typing_rebuild.py)
Automated verification covering Sections A through H:
- Section A: Passage Rendering & Single Authoritative Text Widget
- Section B: Word-Level Commitment & Spacebar Engine
- Section C: Live Character Feedback in Current Word
- Section D: Error Alignment & Cascade Immunity
- Section E: Backspace Intra-Word Editing
- Section F: Native Caret Positioning & No Overlay Frame
- Section G: Session Lifecycle, Timer & Single Storage Save
- Section H: Responsive Viewport Geometry & Content Generation
"""

import unittest
import os
import sys
import tkinter as tk
import time
from typing import Dict, Any, List

# Ensure repository root is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui import theme, scoring, storage
from ui.alignment import TypingAlignmentEngine, levenshtein_align
from ui.content_generator import ContentGenerator
from ui.screens.typing_screen import TypingScreen
from main import TypeRushApp


def safe_destroy(app: TypeRushApp):
    """Safely terminate Tkinter app without orphaned timers."""
    try:
        if hasattr(app, "anim_manager"):
            app.anim_manager.cancel_all()
        for name, screen in getattr(app, "screens", {}).items():
            if hasattr(screen, "cancel_test"):
                screen.cancel_test()
            if hasattr(screen, "timer_after_id") and screen.timer_after_id:
                try:
                    screen.after_cancel(screen.timer_after_id)
                except Exception:
                    pass
            if hasattr(screen, "focus_after_id") and screen.focus_after_id:
                try:
                    screen.after_cancel(screen.focus_after_id)
                except Exception:
                    pass
            if hasattr(screen, "auto_nav_after_id") and screen.auto_nav_after_id:
                try:
                    screen.after_cancel(screen.auto_nav_after_id)
                except Exception:
                    pass
        app.update_idletasks()
        app.destroy()
    except Exception:
        pass


class TestV21TypingRebuild(unittest.TestCase):
    """Exhaustive test suite for TypeRush 2.1 Typing Experience Rebuild."""

    # ========================================================================
    # SECTION A: PASSAGE RENDERING & TEXT WIDGET
    # ========================================================================

    def test_01_single_authoritative_text_widget(self):
        """1. Typing screen contains exactly one Text widget with no overlay frame caret."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]

        self.assertIsInstance(scr.text_display, tk.Text)
        # Verify text display configuration
        self.assertEqual(scr.text_display.cget("wrap"), "word")
        self.assertEqual(scr.text_display.cget("insertwidth"), 2)
        self.assertEqual(scr.text_display.cget("insertbackground"), theme.ACCENT_PRIMARY)

        # Verify no overlay caret is packed or placed on screen
        self.assertEqual(scr.caret.winfo_manager(), "")
        safe_destroy(app)

    def test_02_text_tags_configuration(self):
        """2. Text widget has required semantic tags configured with design tokens."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]

        tags = scr.text_display.tag_names()
        self.assertIn("untyped", tags)
        self.assertIn("correct", tags)
        self.assertIn("incorrect", tags)
        self.assertIn("current_word", tags)
        self.assertIn("current_char_correct", tags)
        self.assertIn("current_char_incorrect", tags)

        self.assertEqual(scr.text_display.tag_cget("untyped", "foreground"), theme.PASSAGE_UNTYPED)
        self.assertEqual(scr.text_display.tag_cget("correct", "foreground"), theme.PASSAGE_CORRECT)
        self.assertEqual(scr.text_display.tag_cget("incorrect", "foreground"), theme.PASSAGE_INCORRECT)
        self.assertEqual(scr.text_display.tag_cget("current_word", "foreground"), theme.PASSAGE_CURRENT_WORD)
        self.assertEqual(scr.text_display.tag_cget("current_char_correct", "foreground"), theme.PASSAGE_CORRECT)
        self.assertEqual(scr.text_display.tag_cget("current_char_incorrect", "foreground"), theme.PASSAGE_INCORRECT)
        safe_destroy(app)

    def test_03_initial_passage_rendering(self):
        """3. Initial buffer has untyped tag and first word has current_word tag."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]

        text_content = scr.text_display.get("1.0", "end-1c")
        self.assertGreater(len(text_content), 100)
        self.assertEqual(text_content, scr.passage_text)

        # First word should have current_word tag
        w_start, w_end = scr.alignment_engine.get_word_span(0)
        word_tags = scr.text_display.tag_names(f"1.0 + {w_start} chars")
        self.assertIn("current_word", word_tags)

        # Later word should have untyped tag
        w2_start, _ = scr.alignment_engine.get_word_span(2)
        word2_tags = scr.text_display.tag_names(f"1.0 + {w2_start} chars")
        self.assertIn("untyped", word2_tags)
        safe_destroy(app)

    def test_04_continuous_buffer_extension(self):
        """4. Buffer extends seamlessly when remaining words drop below threshold."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]

        initial_len = len(scr.alignment_engine.expected_words)
        # Advance current word index to trigger extension
        scr.alignment_engine.current_word_idx = initial_len - 35
        scr._check_and_extend_buffer()

        extended_len = len(scr.alignment_engine.expected_words)
        self.assertGreater(extended_len, initial_len)
        self.assertEqual(scr.text_display.get("1.0", "end-1c"), scr.passage_text)
        safe_destroy(app)

    # ========================================================================
    # SECTION B: WORD-LEVEL COMMITMENT & SPACEBAR ENGINE
    # ========================================================================

    def test_05_spacebar_commits_correct_word_to_green(self):
        """5. Typing a correct word and pressing Space turns entire word green."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]

        first_word = scr.alignment_engine.expected_words[0]
        for char in first_word:
            scr._handle_character(char)
        # Spacebar commits the word
        scr._handle_character(" ")

        self.assertEqual(scr.alignment_engine.current_word_idx, 1)
        self.assertTrue(scr.alignment_engine.is_word_correct(0))

        # Check tag on word 0
        w_start, w_end = scr.alignment_engine.get_word_span(0)
        tags = scr.text_display.tag_names(f"1.0 + {w_start} chars")
        self.assertIn("correct", tags)
        self.assertNotIn("incorrect", tags)
        self.assertNotIn("current_word", tags)
        safe_destroy(app)

    def test_06_spacebar_commits_incorrect_word_to_red(self):
        """6. Typing a misspelled word and pressing Space turns entire word red."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]

        first_word = scr.alignment_engine.expected_words[0]
        # Type deliberate typo
        for char in "xyz123":
            scr._handle_character(char)
        scr._handle_character(" ")

        self.assertEqual(scr.alignment_engine.current_word_idx, 1)
        self.assertFalse(scr.alignment_engine.is_word_correct(0))

        # Check tag on word 0
        w_start, w_end = scr.alignment_engine.get_word_span(0)
        tags = scr.text_display.tag_names(f"1.0 + {w_start} chars")
        self.assertIn("incorrect", tags)
        self.assertNotIn("correct", tags)
        self.assertNotIn("current_word", tags)
        safe_destroy(app)

    def test_07_repeated_space_on_empty_word_ignored(self):
        """7. Space on an empty word does not skip words or runaway."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]

        self.assertEqual(scr.alignment_engine.current_word_idx, 0)
        # Repeated spaces on empty word
        scr._handle_character(" ")
        scr._handle_character(" ")
        scr._handle_character(" ")
        self.assertEqual(scr.alignment_engine.current_word_idx, 0)

        # Type first word correctly and commit
        first_word = scr.alignment_engine.expected_words[0]
        for ch in first_word:
            scr._handle_character(ch)
        scr._handle_character(" ")
        self.assertEqual(scr.alignment_engine.current_word_idx, 1)

        # Repeated spaces on word 1 while empty
        scr._handle_character(" ")
        scr._handle_character(" ")
        self.assertEqual(scr.alignment_engine.current_word_idx, 1)
        safe_destroy(app)

    # ========================================================================
    # SECTION C: LIVE CHARACTER FEEDBACK IN CURRENT WORD
    # ========================================================================

    def test_08_live_character_feedback_in_current_word(self):
        """8. Characters within active word show live green for match and red for typo."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing", custom_text="Practice makes steady progress")
        scr: TypingScreen = app.screens["typing"]

        first_word = scr.alignment_engine.expected_words[0]
        self.assertGreaterEqual(len(first_word), 2)

        # Type first char correctly
        scr._handle_character(first_word[0])
        w_start, _ = scr.alignment_engine.get_word_span(0)
        tags_c0 = scr.text_display.tag_names(f"1.0 + {w_start} chars")
        self.assertIn("current_char_correct", tags_c0)

        # Type second char incorrectly
        wrong_char = "z" if first_word[1].lower() != "z" else "x"
        scr._handle_character(wrong_char)
        tags_c1 = scr.text_display.tag_names(f"1.0 + {w_start + 1} chars")
        self.assertIn("current_char_incorrect", tags_c1)

        # Third char untouched remains current_word
        if len(first_word) > 2:
            tags_c2 = scr.text_display.tag_names(f"1.0 + {w_start + 2} chars")
            self.assertIn("current_word", tags_c2)
            self.assertNotIn("current_char_correct", tags_c2)
            self.assertNotIn("current_char_incorrect", tags_c2)
        safe_destroy(app)

    # ========================================================================
    # SECTION D: ERROR ALIGNMENT & CASCADE IMMUNITY
    # ========================================================================

    def test_09_cascade_immunity_across_words(self):
        """9. Mistake in word N never cascades to ruin word N+1."""
        engine = TypingAlignmentEngine("The quick brown fox jumps")
        # Word 0: "The" (correct)
        for ch in "The ":
            engine.handle_character(ch)
        self.assertTrue(engine.is_word_correct(0))

        # Word 1: "quick" (typo "qwick")
        for ch in "qwick ":
            engine.handle_character(ch)
        self.assertFalse(engine.is_word_correct(1))

        # Word 2: "brown" (correct)
        for ch in "brown ":
            engine.handle_character(ch)
        self.assertTrue(engine.is_word_correct(2))

        # Word 3: "fox" (correct)
        for ch in "fox ":
            engine.handle_character(ch)
        self.assertTrue(engine.is_word_correct(3))

        eval_res = engine.evaluate()
        self.assertEqual(eval_res["correct_words"], 3)
        self.assertEqual(eval_res["incorrect_words"], 1)

    def test_10_case_insensitive_matching(self):
        """10. Case insensitivity treats 'the' and 'THE' as matches."""
        engine = TypingAlignmentEngine("The Quick Brown")
        for ch in "the QUICK brown ":
            engine.handle_character(ch)

        self.assertTrue(engine.is_word_correct(0))
        self.assertTrue(engine.is_word_correct(1))
        self.assertTrue(engine.is_word_correct(2))
        eval_res = engine.evaluate()
        self.assertEqual(eval_res["correct_words"], 3)
        self.assertEqual(eval_res["incorrect_words"], 0)

    def test_11_punctuation_verification(self):
        """11. Punctuation in words is verified accurately."""
        engine = TypingAlignmentEngine("Hello, world!")
        # Correctly type with comma
        for ch in "hello, ":
            engine.handle_character(ch)
        self.assertTrue(engine.is_word_correct(0))

        # Type world without exclamation mark
        for ch in "world ":
            engine.handle_character(ch)
        self.assertFalse(engine.is_word_correct(1))

    # ========================================================================
    # SECTION E: BACKSPACE INTRA-WORD EDITING
    # ========================================================================

    def test_12_backspace_corrects_typo(self):
        """12. Backspace deletes character from current word and restores appearance."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]

        first_word = scr.alignment_engine.expected_words[0]
        # Type correct then typo
        scr._handle_character(first_word[0])
        scr._handle_character("@")
        self.assertEqual(len(scr.alignment_engine.typed_words[0]), 2)

        # Backspace erases typo
        scr._handle_backspace()
        app.update_idletasks()
        self.assertEqual(len(scr.alignment_engine.typed_words[0]), 1)
        self.assertEqual(scr.alignment_engine.typed_words[0], first_word[0])

        w_start, _ = scr.alignment_engine.get_word_span(0)
        tags_c0 = scr.text_display.tag_names(f"1.0 + {w_start} chars")
        self.assertNotIn("current_char_incorrect", tags_c0)
        self.assertIn("current_word", tags_c0)
        safe_destroy(app)

    def test_13_backspace_does_not_modify_committed_words(self):
        """13. Backspace does not spill backward into already committed words."""
        engine = TypingAlignmentEngine("one two three")
        for ch in "one ":
            engine.handle_character(ch)
        self.assertEqual(engine.current_word_idx, 1)

        # Backspace on empty word 1
        engine.handle_backspace()
        engine.handle_backspace()
        self.assertEqual(engine.current_word_idx, 1)
        self.assertEqual(engine.typed_words[0], "one")
        self.assertTrue(engine.is_word_correct(0))

    # ========================================================================
    # SECTION F: NATIVE CARET POSITIONING
    # ========================================================================

    def test_14_native_caret_movement(self):
        """14. Native insertion cursor advances exactly between characters."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing", custom_text="Practice makes steady progress")
        scr: TypingScreen = app.screens["typing"]

        self.assertEqual(scr.text_display.index("insert"), "1.0")

        # Type 3 characters
        first_word = scr.alignment_engine.expected_words[0]
        scr._handle_character(first_word[0])
        self.assertEqual(scr.text_display.index("insert"), "1.1")

        if len(first_word) >= 2:
            scr._handle_character(first_word[1])
            self.assertEqual(scr.text_display.index("insert"), "1.2")

        # Backspace moves caret back
        scr._handle_backspace()
        self.assertEqual(scr.text_display.index("insert"), "1.1")
        safe_destroy(app)

    def test_15_caret_moves_to_next_word_on_space(self):
        """15. Caret jumps cleanly to start of next word upon Space commitment."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]

        first_word = scr.alignment_engine.expected_words[0]
        for ch in first_word:
            scr._handle_character(ch)
        scr._handle_character(" ")

        w1_start, _ = scr.alignment_engine.get_word_span(1)
        expected_index = f"1.{w1_start}"
        self.assertEqual(scr.text_display.index("insert"), expected_index)
        safe_destroy(app)

    # ========================================================================
    # SECTION G: SESSION LIFECYCLE & TIMER
    # ========================================================================

    def test_16_quiet_prompt_disappears_on_keystroke(self):
        """16. Initial quiet prompt disappears completely on first keystroke."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]

        self.assertEqual(scr.prompt_label.cget("text"), "Start typing to begin")
        self.assertEqual(scr.state, "ready")

        # First keystroke
        scr._handle_character("a")
        self.assertEqual(scr.state, "typing")
        self.assertEqual(scr.prompt_label.cget("text"), "")
        safe_destroy(app)

    def test_17_single_storage_save_on_complete(self):
        """17. Test completion saves to storage exactly once."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]

        scr._handle_character("h")
        self.assertEqual(scr.state, "typing")
        scr._complete_test(reason="Time Expired")

        self.assertEqual(scr.state, "completed")
        self.assertTrue(scr.has_saved_current_session)
        res_id = scr.last_result["id"]

        # Multiple complete calls do not duplicate save
        scr._complete_test(reason="Time Expired")
        self.assertEqual(scr.last_result["id"], res_id)
        safe_destroy(app)

    # ========================================================================
    # SECTION H: RESPONSIVE VIEWPORT & CONTENT CURATION
    # ========================================================================

    def test_18_no_duplicate_sentences_in_deck(self):
        """18. Content generator deck never yields consecutive duplicate sentences."""
        gen = ContentGenerator(seed=123)
        seen = []
        for _ in range(30):
            sentence = gen._get_next_sentence(gen._curated_sentences if hasattr(gen, "_curated_sentences") else gen.generate_chunk(10).split(". "))
            if seen:
                self.assertNotEqual(sentence, seen[-1])
            seen.append(sentence)

    def test_19_header_branding_without_midnight_minimal_badge(self):
        """19. Header branding displays clean title and metadata without redundant badge."""
        app = TypeRushApp()
        app.withdraw()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]

        self.assertIn("CHALLENGE", scr.meta_label.cget("text"))
        # Verify no edition_badge is packed in session_header
        self.assertFalse(hasattr(scr, "edition_badge") and scr.edition_badge.winfo_manager() != "")
        safe_destroy(app)

    def test_20_responsive_resize_1200_and_950(self):
        """20. Layout remains stable across 1200x800 and 950x650 viewport sizes."""
        app = TypeRushApp()
        app.withdraw()

        # Test at 1200x800
        app.geometry("1200x800")
        app.update()
        app.show_screen("typing")
        scr: TypingScreen = app.screens["typing"]
        app.update()
        self.assertGreater(scr.passage_wrapper.winfo_width(), 700)

        # Test at 950x650
        app.geometry("950x650")
        app.update()
        self.assertGreater(scr.passage_wrapper.winfo_width(), 600)
        safe_destroy(app)


if __name__ == "__main__":
    unittest.main()
