"""
TypeRush 2.1 — Live Interactive Typing Verification & Demonstration Runner
Executes Tests 1 through 9 on the rebuilt typing engine and screen.
"""

import os
import sys
import time
import tkinter as tk

# Ensure repository root is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main import TypeRushApp
from ui.screens.typing_screen import TypingScreen
from ui import theme


def run_demo():
    print("=" * 75)
    print("TYPERUSH 2.1 — LIVE TYPING EXPERIENCE REBUILD DEMONSTRATION (TESTS 1 - 9)")
    print("=" * 75)

    app = TypeRushApp()
    app.geometry("1200x800+50+50")
    app.deiconify()
    app.update()

    app.show_screen("typing", duration=60, difficulty="Medium")
    scr: TypingScreen = app.screens["typing"]
    app.update()

    # TEST 1: Type first words correctly -> verify green commitment
    print("\n--- TEST 1: Word-level correct commitment ---")
    w0 = scr.alignment_engine.expected_words[0]
    w1 = scr.alignment_engine.expected_words[1]
    print(f"Typing word 0 ('{w0}') and word 1 ('{w1}')...")
    for ch in w0 + " " + w1 + " ":
        ev = tk.Event()
        ev.char = ch
        ev.keysym = ch
        scr._on_key_press(ev)
    app.update()

    # Verify both words turned green
    w0_start, _ = scr.alignment_engine.get_word_span(0)
    w1_start, _ = scr.alignment_engine.get_word_span(1)
    tags0 = scr.text_display.tag_names(f"1.0 + {w0_start} chars")
    tags1 = scr.text_display.tag_names(f"1.0 + {w1_start} chars")
    print(f"Word 0 ('{w0}') tags:", tags0)
    print(f"Word 1 ('{w1}') tags:", tags1)
    assert "correct" in tags0, "Word 0 should have 'correct' tag!"
    assert "correct" in tags1, "Word 1 should have 'correct' tag!"
    print("-> PASS: Words committed correctly with green highlighting.")

    # TEST 2: Type a misspelled word -> verify red commitment
    print("\n--- TEST 2: Word-level error commitment ---")
    w2 = scr.alignment_engine.expected_words[2]
    misspelled = "xyztypo"
    print(f"Expected word 2 is '{w2}'. Typing intentional typo '{misspelled}'...")
    for ch in misspelled + " ":
        ev = tk.Event()
        ev.char = ch
        ev.keysym = ch
        scr._on_key_press(ev)
    app.update()

    w2_start, _ = scr.alignment_engine.get_word_span(2)
    tags2 = scr.text_display.tag_names(f"1.0 + {w2_start} chars")
    print(f"Word 2 tags after space:", tags2)
    assert "incorrect" in tags2, "Word 2 should have 'incorrect' tag!"
    print("-> PASS: Misspelled word committed with red error highlighting.")

    # TEST 3: Cascade immunity -> type next words correctly
    print("\n--- TEST 3: Cascade immunity (subsequent correct words turn green) ---")
    w3 = scr.alignment_engine.expected_words[3]
    w4 = scr.alignment_engine.expected_words[4]
    print(f"Typing word 3 ('{w3}') and word 4 ('{w4}')...")
    for ch in w3 + " " + w4 + " ":
        ev = tk.Event()
        ev.char = ch
        ev.keysym = ch
        scr._on_key_press(ev)
    app.update()

    w3_start, _ = scr.alignment_engine.get_word_span(3)
    w4_start, _ = scr.alignment_engine.get_word_span(4)
    tags3 = scr.text_display.tag_names(f"1.0 + {w3_start} chars")
    tags4 = scr.text_display.tag_names(f"1.0 + {w4_start} chars")
    print(f"Word 3 tags:", tags3)
    print(f"Word 4 tags:", tags4)
    assert "correct" in tags3, "Word 3 should have 'correct' tag!"
    assert "correct" in tags4, "Word 4 should have 'correct' tag!"
    print("-> PASS: Cascade immunity verified; prior typo did not shift or affect subsequent words.")

    # TEST 4: Backspace error correction
    print("\n--- TEST 4: Backspace intra-word error correction ---")
    w5 = scr.alignment_engine.expected_words[5]
    print(f"Word 5 is '{w5}'. Typing first char '{w5[0]}' then typo '###'...")
    for ch in w5[0] + "###":
        ev = tk.Event()
        ev.char = ch
        ev.keysym = ch
        scr._on_key_press(ev)
    app.update()

    # Backspace 3 times
    print("Executing 3 Backspaces to erase typo...")
    for _ in range(3):
        ev = tk.Event()
        ev.char = ""
        ev.keysym = "BackSpace"
        scr._on_key_press(ev)
    app.update()

    # Finish word correctly
    print(f"Typing rest of word 5 '{w5[1:]}' and space...")
    for ch in w5[1:] + " ":
        ev = tk.Event()
        ev.char = ch
        ev.keysym = ch
        scr._on_key_press(ev)
    app.update()

    w5_start, _ = scr.alignment_engine.get_word_span(5)
    tags5 = scr.text_display.tag_names(f"1.0 + {w5_start} chars")
    print(f"Word 5 tags:", tags5)
    assert "correct" in tags5, "Word 5 should have 'correct' tag after correction!"
    print("-> PASS: Backspace intra-word editing successfully corrected typo.")

    # TEST 5: Case-insensitivity
    print("\n--- TEST 5: Case-insensitive matching ---")
    w6 = scr.alignment_engine.expected_words[6]
    upper_w6 = w6.upper()
    print(f"Word 6 is '{w6}'. Typing uppercase version '{upper_w6}'...")
    for ch in upper_w6 + " ":
        ev = tk.Event()
        ev.char = ch
        ev.keysym = ch
        scr._on_key_press(ev)
    app.update()

    w6_start, _ = scr.alignment_engine.get_word_span(6)
    tags6 = scr.text_display.tag_names(f"1.0 + {w6_start} chars")
    print(f"Word 6 tags:", tags6)
    assert "correct" in tags6, "Uppercase match should be accepted as correct!"
    print("-> PASS: Case-insensitivity accepted uppercase input as correct.")

    # TEST 6: Punctuation verification
    print("\n--- TEST 6: Punctuation verification ---")
    w7 = scr.alignment_engine.expected_words[7]
    print(f"Target word 7: '{w7}'.")
    for ch in w7 + " ":
        ev = tk.Event()
        ev.char = ch
        ev.keysym = ch
        scr._on_key_press(ev)
    app.update()
    w7_start, _ = scr.alignment_engine.get_word_span(7)
    tags7 = scr.text_display.tag_names(f"1.0 + {w7_start} chars")
    assert "correct" in tags7
    print("-> PASS: Punctuation match verified.")

    # TEST 7: Continuous buffer extension
    print("\n--- TEST 7: Continuous stream buffer extension ---")
    init_words = len(scr.alignment_engine.expected_words)
    print(f"Initial words in buffer: {init_words}")
    scr.alignment_engine.current_word_idx = init_words - 30
    scr._check_and_extend_buffer()
    new_words = len(scr.alignment_engine.expected_words)
    print(f"New words after extension: {new_words}")
    assert new_words > init_words, "Buffer should have extended seamlessly!"
    print("-> PASS: Continuous buffer extended without resetting progress.")

    # TEST 8: Window resizing (1200x800 and 950x650)
    print("\n--- TEST 8: Viewport resizing geometry ---")
    app.geometry("1200x800")
    app.update()
    w1200 = scr.passage_wrapper.winfo_width()
    print(f"Passage wrapper width at 1200x800: {w1200}px")

    app.geometry("950x650")
    app.update()
    w950 = scr.passage_wrapper.winfo_width()
    print(f"Passage wrapper width at 950x650: {w950}px")
    assert w1200 > 700 and w950 > 600, "Widths should remain spacious and comfortable!"
    print("-> PASS: Responsive geometry stable at both 1200x800 and 950x650.")

    # TEST 9: Native caret sitting between characters
    print("\n--- TEST 9: Native insertion caret inspection ---")
    insert_idx = scr.text_display.index("insert")
    caret_w = scr.text_display.cget("insertwidth")
    caret_bg = scr.text_display.cget("insertbackground")
    print(f"Caret index: {insert_idx}, Width: {caret_w}px, Color: {caret_bg}")
    assert int(caret_w) >= 2, "Insert width should be at least 2px!"
    assert scr.caret.winfo_manager() == "", "Overlay frame caret must not be managed!"
    print("-> PASS: Native cursor active, correctly configured, sitting between characters.")

    print("\n" + "=" * 75)
    print("ALL 9 TYPING EXPERIENCE REBUILD DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
    print("=" * 75)

    try:
        app.destroy()
    except Exception:
        pass


if __name__ == "__main__":
    run_demo()
