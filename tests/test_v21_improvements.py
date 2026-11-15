"""
Unit Tests for TypeRush 2.1 Feature Enhancements

Tests:
1. Window icon asset presence and format verification
2. Content generator Code difficulty passages
3. Custom text setting, looping, and clearing
4. Weak key practice generator scoring and generation
5. Alignment engine weak key tracking on mistakes
6. Scoring engine weak key passthrough in metrics & session result
7. JSON history export and import merging without duplicate IDs
8. Master mode setting loading, defaults, and persistence
9. Audio dispatcher cross-platform handling
"""

import os
import sys
import json
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui import storage, scoring
from ui.alignment import TypingAlignmentEngine
from ui.content_generator import ContentGenerator
from ui.audio_manager import AudioManager


class TestTypeRushImprovements(unittest.TestCase):

    def test_01_window_icon_asset_valid(self):
        """Verify assets/icons/app.ico exists and has valid ICO header."""
        ico_path = os.path.join(BASE_DIR, "assets", "icons", "app.ico")
        self.assertTrue(os.path.isfile(ico_path))
        with open(ico_path, "rb") as f:
            header = f.read(4)
        # Reserved 0x0000, Type 0x0001
        self.assertEqual(header, b"\x00\x00\x01\x00")

    def test_02_content_generator_code_tier(self):
        """Verify Code tier exists and produces programming syntax chunks."""
        gen = ContentGenerator(difficulty="Code")
        chunk = gen.generate_chunk(word_target=20)
        self.assertIsInstance(chunk, str)
        self.assertGreater(len(chunk), 10)
        # Verify presence of code tokens
        has_code_tokens = any(ch in chunk for ch in ("{", "}", "=", ";", "(", ")"))
        self.assertTrue(has_code_tokens)

    def test_03_custom_text_injection(self):
        """Verify custom text can be injected, retrieved, and cleared."""
        gen = ContentGenerator()
        custom = "The quick brown fox jumps over the lazy dog."
        gen.set_custom_text(custom)
        chunk = gen.generate_chunk(word_target=9)
        self.assertEqual(chunk, custom)

        # Clear custom text resumes normal generation
        gen.clear_custom_text()
        normal_chunk = gen.generate_chunk(word_target=10)
        self.assertNotEqual(normal_chunk, custom)

    def test_04_weak_key_practice_generator(self):
        """Verify weak key generator generates passages emphasizing specific characters."""
        gen = ContentGenerator()
        weak_keys = ["z", "q", "x"]
        passage = gen.generate_weak_key_practice(weak_keys, word_target=30)
        self.assertIsInstance(passage, str)
        self.assertGreater(len(passage.split()), 10)

    def test_05_alignment_engine_weak_key_tracking(self):
        """Verify TypingAlignmentEngine tracks error frequency per character."""
        engine = TypingAlignmentEngine("hello world")
        # Type "hx" instead of "he"
        engine.handle_character("h")
        engine.handle_character("x")
        engine.handle_character("l")
        engine.handle_character("l")
        engine.handle_character("o")
        engine.handle_character(" ")
        
        eval_res = engine.evaluate()
        self.assertIn("weak_keys", eval_res)
        weak_keys = eval_res["weak_keys"]
        # 'e' was missed or 'x' was inserted
        self.assertTrue("e" in weak_keys or "x" in weak_keys)

    def test_06_scoring_metrics_weak_keys_passthrough(self):
        """Verify calculate_typing_metrics includes weak_keys in output."""
        wk = {"p": 2, ";": 1}
        metrics = scoring.calculate_typing_metrics(
            correct_chars=50,
            incorrect_chars=3,
            total_typed=53,
            elapsed_seconds=30.0,
            weak_keys=wk
        )
        self.assertIn("weak_keys", metrics)
        self.assertEqual(metrics["weak_keys"], wk)

    def test_07_json_backup_export_and_import(self):
        """Verify JSON export and import seamlessly roundtrips without duplicate IDs."""
        test_export_path = os.path.join(BASE_DIR, "data", "test_temp_backup.json")
        try:
            ok, export_path = storage.export_history_to_json(test_export_path)
            self.assertTrue(ok)
            self.assertTrue(os.path.isfile(test_export_path))

            # Validate valid JSON content
            with open(test_export_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIsInstance(data, list)

            # Test import
            ok_imp, added, msg = storage.import_history_from_json(test_export_path)
            self.assertTrue(ok_imp)
            # Since IDs already exist, duplicate addition is prevented (added == 0)
            self.assertEqual(added, 0)
        finally:
            if os.path.isfile(test_export_path):
                os.remove(test_export_path)

    def test_08_master_mode_setting_persistence(self):
        """Verify master_mode preference exists in defaults and persists properly."""
        orig_settings = storage.load_settings()
        try:
            self.assertIn("master_mode", orig_settings)
            
            orig_settings["master_mode"] = True
            storage.save_settings(orig_settings)
            reloaded = storage.load_settings()
            self.assertTrue(reloaded["master_mode"])
        finally:
            orig_settings["master_mode"] = False
            storage.save_settings(orig_settings)

    def test_09_audio_manager_safe_cross_platform(self):
        """Verify audio manager does not crash on non-blocking playback calls."""
        audio = AudioManager()
        audio._test_mode = True
        audio._play_file("key_tap.wav")
        audio._play_file("ui_click.wav")
        self.assertGreater(len(audio._played_log), 0)
        self.assertIn("key_tap.wav", audio._played_log)


if __name__ == "__main__":
    unittest.main()
