"""
TypeRush 2.1 Visual Verification & Official Screenshot Suite
Captures genuine, pixel-perfect offscreen GDI screenshots of the completed TypeRush 2.1 application.

Required screenshots (saved to screenshots/v2.1/ and artifact directory):
1. 01_home_dashboard.png: Home Dashboard at 1200x800 showing Midnight Minimal, Quick Start, no mode selector.
2. 02_typing_untouched.png: Typing Screen at 1200x800 untouched grey characters & vertical caret.
3. 03_typing_correct_green.png: Typing Screen with immediately highlighted green characters.
4. 04_typing_incorrect_red.png: Typing Screen with mistake characters highlighted red.
5. 05_typing_corrected_word.png: Typing Screen showing word corrected via Backspace.
6. 06_exit_confirmation_modal.png: Typing Screen with compact (~420x175 px) top-right confirmation modal.
7. 07_results_screen.png: Redesigned Results screen with Net WPM hero, metrics grid, progression curve.
8. 08_mistake_review.png: Results screen scrolled to Mistake Review section showing word differences.
9. 09_history_screen.png: History screen timeline, filters, and personal best badge.
10. 10_settings_screen.png: Redesigned Settings screen with wide 220px sidebar (no clipping) and General category.
"""

import os
import sys
import time
import zlib
import struct
import ctypes
from ctypes import wintypes
import shutil
import tkinter as tk

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

PW_RENDERFULLCONTENT = 2


def get_window_pixels(hwnd: int):
    """Retrieve raw 32-bit BGRA pixel bytes and dimensions directly from HWND."""
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w = max(1, rect.right - rect.left)
    h = max(1, rect.bottom - rect.top)

    hdc_screen = user32.GetDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
    hbm = gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
    gdi32.SelectObject(hdc_mem, hbm)

    res = user32.PrintWindow(hwnd, hdc_mem, PW_RENDERFULLCONTENT)
    if not res:
        user32.PrintWindow(hwnd, hdc_mem, 0)

    bmi = bytearray(40)
    struct.pack_into("<IiiHHIIIIII", bmi, 0, 40, w, -h, 1, 32, 0, w * h * 4, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(hdc_mem, hbm, 0, h, buf, bytes(bmi), 0)

    gdi32.DeleteObject(hbm)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(hwnd, hdc_screen)
    return w, h, bytearray(buf)


def composite_windows(root_hwnd: int, child_hwnd: int):
    """Composite child toplevel onto root window pixels at its relative position."""
    r_rect = wintypes.RECT()
    c_rect = wintypes.RECT()
    user32.GetWindowRect(root_hwnd, ctypes.byref(r_rect))
    user32.GetWindowRect(child_hwnd, ctypes.byref(c_rect))

    rw, rh, r_bytes = get_window_pixels(root_hwnd)
    cw, ch, c_bytes = get_window_pixels(child_hwnd)

    ox = c_rect.left - r_rect.left
    oy = c_rect.top - r_rect.top

    # Stamp child pixels over root pixels
    for cy in range(ch):
        ty = oy + cy
        if 0 <= ty < rh:
            for cx in range(cw):
                tx = ox + cx
                if 0 <= tx < rw:
                    src_idx = (cy * cw + cx) * 4
                    dst_idx = (ty * rw + tx) * 4
                    r_bytes[dst_idx : dst_idx + 4] = c_bytes[src_idx : src_idx + 4]

    return rw, rh, r_bytes


def save_raw_pixels_to_png(w: int, h: int, raw_bytes: bytearray, out_path: str):
    """Save 32-bit BGRA buffer as compressed PNG file."""
    scanlines = []
    stride = w * 4
    for y in range(h):
        line = bytearray(1 + stride)
        line[0] = 0
        row = raw_bytes[y * stride : (y + 1) * stride]
        for x in range(0, stride, 4):
            line[1 + x] = row[x + 2]      # R
            line[1 + x + 1] = row[x + 1]  # G
            line[1 + x + 2] = row[x]      # B
            line[1 + x + 3] = 255         # A
        scanlines.append(line)

    compressed = zlib.compress(b"".join(scanlines))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        crc = zlib.crc32(tag + data) & 0xffffffff
        return c + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    png_data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(png_data)


def capture_v21_visuals():
    print("=" * 70)
    print("TYPERUSH 2.1 REDESIGN — OFFICIAL VERIFICATION SCREENSHOT SUITE")
    print("=" * 70)

    from ui.app import TypeRushApp
    from ui import storage, theme
    from ui.screens.home_screen import HomeScreen
    from ui.screens.typing_screen import TypingScreen
    from ui.screens.results_screen import ResultsScreen
    from ui.screens.history_screen import HistoryScreen
    from ui.screens.settings_screen import SettingsScreen

    # Prepare directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    v21_dir = os.path.join(base_dir, "screenshots", "v2.1")
    artifact_dir = r"C:\Users\wisep\.gemini\antigravity\brain\eebfc68b-b506-4a91-bb33-60d0b372eb4d"
    os.makedirs(v21_dir, exist_ok=True)
    os.makedirs(artifact_dir, exist_ok=True)

    # Initialize app with 1200x800 resolution
    app = TypeRushApp()
    app.geometry("1200x800+40+40")
    app.deiconify()
    app.update()

    def snapshot(filename: str, modal_hwnd: int = 0):
        app.update_idletasks()
        app.update()
        time.sleep(0.15)
        local_path = os.path.join(v21_dir, filename)
        art_path = os.path.join(artifact_dir, filename)

        if modal_hwnd:
            w, h, raw = composite_windows(app.winfo_id(), modal_hwnd)
            save_raw_pixels_to_png(w, h, raw, local_path)
        else:
            w, h, raw = get_window_pixels(app.winfo_id())
            save_raw_pixels_to_png(w, h, raw, local_path)

        shutil.copyfile(local_path, art_path)
        print(f"[Captured] {filename} ({os.path.getsize(local_path)} bytes)", flush=True)

    # -------------------------------------------------------------------------
    # 1. 01_home_dashboard.png
    # -------------------------------------------------------------------------
    print("\n[Step 1/10] Capturing Home Dashboard...", flush=True)
    app.show_screen("home")
    app.update()
    snapshot("01_home_dashboard.png")

    # -------------------------------------------------------------------------
    # 2. 02_typing_untouched.png
    # -------------------------------------------------------------------------
    print("\n[Step 2/10] Capturing Typing Screen (untouched)...", flush=True)
    app.show_screen("typing", difficulty="Medium", duration=60)
    typing_scr: TypingScreen = app.screens["typing"]
    app.update()
    snapshot("02_typing_untouched.png")

    # -------------------------------------------------------------------------
    # 3. 03_typing_correct_green.png
    # -------------------------------------------------------------------------
    print("\n[Step 3/10] Capturing Typing Screen (green character highlighting)...", flush=True)
    # Type the first 35 characters of the target passage accurately
    target = typing_scr.passage_text
    sample_correct = target[:30]
    for ch in sample_correct:
        ev = tk.Event()
        ev.char = ch
        ev.keysym = ch
        typing_scr._on_key_press(ev)
    app.update()
    snapshot("03_typing_correct_green.png")

    # -------------------------------------------------------------------------
    # 4. 04_typing_incorrect_red.png
    # -------------------------------------------------------------------------
    print("\n[Step 4/10] Capturing Typing Screen (red mistake character highlighting)...", flush=True)
    # Type 4 deliberate error characters
    for ch in "zzxx":
        ev = tk.Event()
        ev.char = ch
        ev.keysym = ch
        typing_scr._on_key_press(ev)
    app.update()
    snapshot("04_typing_incorrect_red.png")

    # -------------------------------------------------------------------------
    # 5. 05_typing_corrected_word.png
    # -------------------------------------------------------------------------
    print("\n[Step 5/10] Capturing Typing Screen (word corrected with Backspace)...", flush=True)
    # Backspace out the 4 errors
    for _ in range(4):
        ev = tk.Event()
        ev.char = ""
        ev.keysym = "BackSpace"
        typing_scr._on_key_press(ev)
    # Type next 10 correct characters from target
    corrected_sub = target[30:40]
    for ch in corrected_sub:
        ev = tk.Event()
        ev.char = ch
        ev.keysym = ch
        typing_scr._on_key_press(ev)
    app.update()
    snapshot("05_typing_corrected_word.png")

    # -------------------------------------------------------------------------
    # 6. 06_exit_confirmation_modal.png
    # -------------------------------------------------------------------------
    print("\n[Step 6/10] Capturing Exit Confirmation Modal...", flush=True)
    # Enable confirm_exit in settings
    s = storage.load_settings()
    s["confirm_exit"] = True
    storage.save_settings(s)

    typing_scr.request_exit(action="home")
    app.update()
    dialog_hwnd = typing_scr.exit_dialog.winfo_id() if typing_scr.exit_dialog else 0
    snapshot("06_exit_confirmation_modal.png", modal_hwnd=dialog_hwnd)

    # Dismiss dialog and resume
    if typing_scr.exit_dialog:
        typing_scr.exit_dialog.destroy()
        typing_scr.exit_dialog = None
    typing_scr._resume_timer()
    app.update()

    # Reset confirm_exit back to default False
    s["confirm_exit"] = False
    storage.save_settings(s)

    # -------------------------------------------------------------------------
    # 7. 07_results_screen.png
    # -------------------------------------------------------------------------
    print("\n[Step 7/10] Capturing Results Screen...", flush=True)
    typing_scr._complete_test(reason="Time Expired")
    app.update()
    time.sleep(0.35)
    app.update()
    snapshot("07_results_screen.png")

    # -------------------------------------------------------------------------
    # 8. 08_mistake_review.png
    # -------------------------------------------------------------------------
    print("\n[Step 8/10] Capturing Mistake Review section...", flush=True)
    results_scr: ResultsScreen = app.screens["results"]
    # Scroll canvas to reveal Section E: Mistake Review & Alignment
    results_scr.scroll_canvas.yview_moveto(0.55)
    app.update()
    snapshot("08_mistake_review.png")

    # -------------------------------------------------------------------------
    # 9. 09_history_screen.png
    # -------------------------------------------------------------------------
    print("\n[Step 9/10] Capturing History Screen...", flush=True)
    app.show_screen("history")
    app.update()
    snapshot("09_history_screen.png")

    # -------------------------------------------------------------------------
    # 10. 10_settings_screen.png
    # -------------------------------------------------------------------------
    print("\n[Step 10/10] Capturing Settings Screen (General category)...", flush=True)
    app.show_screen("settings")
    settings_scr: SettingsScreen = app.screens["settings"]
    settings_scr._switch_category("general")
    app.update()
    snapshot("10_settings_screen.png")

    print("\n" + "=" * 70)
    print("ALL 10 VERIFICATION SCREENSHOTS CAPTURED SUCCESSFULLY!")
    print(f"Destination: {v21_dir}")
    print("=" * 70)

    try:
        app.destroy()
    except Exception:
        pass


if __name__ == "__main__":
    capture_v21_visuals()
