"""
TypeRush 2.0 Audio Manager

Native Python standard-library audio architecture for TypeRush 2.0 (Midnight Studio).
Provides responsive, restrained, and elegant audio feedback for:
- Soft mechanical keystrokes (throttled to avoid rapid-typing distortion)
- Clean UI interactions (buttons, navigation, modals)
- Satisfying session completion chimes
- Subtle, non-punitive error cues

Audio Edition Rules:
- BASIC EDITION: Hard muted under all circumstances. Never plays sound.
- PLEASANT EDITION: Sound is OFF by default on fresh install; explicit user choices are respected.
- SOUNDSCAPE EDITION: Sound is ON by default on fresh install; subtle auditory environment.
- Preference Persistence: Explicit mute or volume settings are never silently overwritten
  when switching editions.
"""

import os
import sys
import math
import struct
import wave
import time
import random
from typing import Optional, Dict, Any, List

# Standard library sound playback on Windows
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    winsound = None
    HAS_WINSOUND = False

from ui import storage


class AudioManager:
    """
    Central sound controller for TypeRush 2.0.
    Handles synthesis of standard WAV assets, volume scaling,
    throttling, edition policy enforcement, and non-blocking playback.
    """

    def __init__(self, app: Optional[Any] = None, assets_dir: Optional[str] = None):
        self.app = app
        self._test_mode: bool = False
        self._played_log: List[str] = []
        self._last_keypress_time: float = 0.0
        self._min_keypress_interval: float = 0.040  # 40ms throttle (~25 keystrokes/sec max)

        # Base sound assets directory
        if assets_dir:
            self.assets_dir = assets_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.assets_dir = os.path.join(base_dir, "assets", "sounds")

        os.makedirs(self.assets_dir, exist_ok=True)

        # Load persisted preferences
        settings = storage.load_settings()
        self.master_enabled: bool = bool(settings.get("sound_enabled", False))
        self.volume: int = max(0, min(100, int(settings.get("sound_volume", 70))))
        self.sound_keypress: bool = bool(settings.get("sound_keypress", True))
        self.sound_ui_click: bool = bool(settings.get("sound_ui_click", True))
        self.sound_completion: bool = bool(settings.get("sound_completion", True))
        self.sound_error: bool = bool(settings.get("sound_error", False))

        # Ensure all 5 sound WAV assets are generated
        self.ensure_sound_assets()

    # ========================================================================
    # SOUND SYNTHESIS (Offline Native 16-bit PCM WAV)
    # ========================================================================

    def ensure_sound_assets(self) -> None:
        """
        Verify that all 5 core sound WAV assets exist.
        If missing, generate them offline using pure standard library mathematics.
        """
        required_sounds = {
            "key_tap.wav": self._synthesize_key_tap,
            "ui_click.wav": self._synthesize_ui_click,
            "navigation.wav": self._synthesize_navigation,
            "completion.wav": self._synthesize_completion,
            "soft_error.wav": self._synthesize_soft_error,
        }

        for filename, synth_fn in required_sounds.items():
            path = os.path.join(self.assets_dir, filename)
            if not os.path.isfile(path) or os.path.getsize(path) < 100:
                try:
                    synth_fn(path)
                except Exception:
                    pass

    def _write_wav_file(self, filepath: str, samples: List[float], sample_rate: int = 44100) -> None:
        """Write floating-point samples [-1.0, 1.0] to a 16-bit mono PCM WAV file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            packed = [
                struct.pack("<h", max(-32768, min(32767, int(s * 32767.0))))
                for s in samples
            ]
            wf.writeframes(b"".join(packed))

    def _synthesize_key_tap(self, filepath: str) -> None:
        """Soft mechanical key tap (~28ms, gentle dampened switch sound)."""
        sr = 44100
        dur = 0.028
        n = int(sr * dur)
        samples = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t / 0.006)
            noise = (random.random() * 2.0 - 1.0) * math.exp(-t / 0.003) * 0.15
            tone = math.sin(2.0 * math.pi * (460.0 - 240.0 * (t / dur)) * t) * 0.25
            samples.append((tone + noise) * env)
        self._write_wav_file(filepath, samples, sr)

    def _synthesize_ui_click(self, filepath: str) -> None:
        """Subtle tactile UI click (~18ms, 950Hz micro-tick)."""
        sr = 44100
        dur = 0.018
        n = int(sr * dur)
        samples = []
        for i in range(n):
            t = i / sr
            env = math.exp(-t / 0.004)
            samples.append(math.sin(2.0 * math.pi * 950.0 * t) * 0.30 * env)
        self._write_wav_file(filepath, samples, sr)

    def _synthesize_navigation(self, filepath: str) -> None:
        """Soft rising navigation swoosh (~35ms)."""
        sr = 44100
        dur = 0.035
        n = int(sr * dur)
        samples = []
        for i in range(n):
            t = i / dur
            freq = 320.0 + 260.0 * t
            env = math.sin(math.pi * t)
            samples.append(math.sin(2.0 * math.pi * freq * (i / sr)) * 0.22 * env)
        self._write_wav_file(filepath, samples, sr)

    def _synthesize_completion(self, filepath: str) -> None:
        """Warm, crystalline harmonic major chord (C5-E5-G5-C6) with 360ms decay."""
        sr = 44100
        dur = 0.360
        n = int(sr * dur)
        samples = []
        for i in range(n):
            t = i / sr
            attack = min(1.0, t / 0.015)
            env = attack * math.exp(-t / 0.09)
            c5 = 0.30 * math.sin(2.0 * math.pi * 523.25 * t)
            e5 = 0.25 * math.sin(2.0 * math.pi * 659.25 * t)
            g5 = 0.22 * math.sin(2.0 * math.pi * 783.99 * t)
            c6 = 0.15 * math.sin(2.0 * math.pi * 1046.50 * t)
            samples.append((c5 + e5 + g5 + c6) * env)
        self._write_wav_file(filepath, samples, sr)

    def _synthesize_soft_error(self, filepath: str) -> None:
        """Subtle non-punitive double-tap cue (55ms)."""
        sr = 44100
        dur = 0.055
        n = int(sr * dur)
        samples = []
        for i in range(n):
            t = i / sr
            if t < 0.020:
                env = math.exp(-t / 0.006)
                samples.append(math.sin(2.0 * math.pi * 180.0 * t) * 0.24 * env)
            elif 0.030 <= t < 0.050:
                t2 = t - 0.030
                env = math.exp(-t2 / 0.006)
                samples.append(math.sin(2.0 * math.pi * 160.0 * t2) * 0.20 * env)
            else:
                samples.append(0.0)
        self._write_wav_file(filepath, samples, sr)

    # ========================================================================
    # EDITION RULES & AUDIO POLICIES
    # ========================================================================

    def get_edition(self) -> str:
        """Retrieve the currently active visual edition key."""
        if self.app and hasattr(self.app, "edition_manager"):
            return self.app.edition_manager.get_current_edition()
        settings = storage.load_settings()
        return settings.get("edition", "pleasant")

    def is_edition_silent(self) -> bool:
        """
        Evaluate if current edition strictly prohibits audio.
        BASIC edition is ALWAYS hard muted under every circumstance.
        """
        return self.get_edition() == "basic"

    def is_sound_active(self) -> bool:
        """
        Comprehensive check if sound is globally permitted:
        - Must not be Basic Edition
        - Master sound must be enabled
        - Volume must be > 0
        """
        if self.is_edition_silent():
            return False

        if self.app and hasattr(self.app, "edition_manager"):
            if not self.app.edition_manager.is_sound_enabled():
                return False
        elif not self.master_enabled:
            return False

        if self.volume <= 0:
            return False

        return True

    def can_play(self, sound_type: str = "general") -> bool:
        """
        Evaluate if a specific sound type can play right now.
        Checks edition silence, master mute, volume, and individual preference.
        """
        if not self.is_sound_active():
            return False

        if sound_type == "keypress" and not self.sound_keypress:
            return False
        if sound_type in ("ui_click", "click") and not self.sound_ui_click:
            return False
        if sound_type == "navigation" and not self.sound_ui_click:
            return False
        if sound_type == "completion" and not self.sound_completion:
            return False
        if sound_type == "error" and not self.sound_error:
            return False

        return True

    # ========================================================================
    # PLAYBACK ENGINE
    # ========================================================================

    def _play_file(self, filename: str) -> None:
        """Play a WAV file asynchronously without blocking the GUI or input event loop."""
        self._played_log.append(filename)

        if self._test_mode:
            return

        filepath = os.path.join(self.assets_dir, filename)
        if not os.path.isfile(filepath):
            # Attempt to re-generate if missing
            self.ensure_sound_assets()
            if not os.path.isfile(filepath):
                return

        # 1. Windows native asynchronous playback
        if HAS_WINSOUND and winsound is not None:
            try:
                winsound.PlaySound(
                    filepath,
                    winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
                )
                return
            except Exception:
                pass

        # 2. Cross-platform fallback for macOS (afplay) and Linux (paplay/aplay)
        try:
            import shutil
            import subprocess
            if sys.platform == "darwin" and shutil.which("afplay"):
                subprocess.Popen(["afplay", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif sys.platform.startswith("linux"):
                if shutil.which("paplay"):
                    subprocess.Popen(["paplay", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif shutil.which("aplay"):
                    subprocess.Popen(["aplay", "-q", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def play_keypress(self) -> None:
        """Play mechanical keystroke sound with throttling."""
        now = time.time()
        if now - self._last_keypress_time < self._min_keypress_interval:
            return  # Throttle rapid keystrokes to prevent distortion
        self._last_keypress_time = now

        if self.can_play("keypress"):
            self._play_file("key_tap.wav")

    def play_ui_click(self) -> None:
        """Play subtle UI interaction sound."""
        if self.can_play("ui_click"):
            self._play_file("ui_click.wav")

    def play_navigation(self) -> None:
        """Play smooth navigation transition sound."""
        if self.can_play("navigation"):
            self._play_file("navigation.wav")

    def play_completion(self) -> None:
        """Play satisfying test completion chime."""
        if self.can_play("completion"):
            self._play_file("completion.wav")

    def play_error(self) -> None:
        """Play subtle non-punitive error cue."""
        if self.can_play("error"):
            self._play_file("soft_error.wav")

    def preview_sound(self, sound_name: str) -> bool:
        """
        Preview a sound explicitly requested by the user.
        Respects active edition silence (Basic is muted) and master mute,
        but bypasses individual category toggle for previewing.
        Returns True if played, False if blocked.
        """
        if self.is_edition_silent():
            return False

        if self.app and hasattr(self.app, "edition_manager"):
            if not self.app.edition_manager.is_sound_enabled():
                return False
        elif not self.master_enabled:
            return False

        sound_map = {
            "keypress": "key_tap.wav",
            "key_tap": "key_tap.wav",
            "ui_click": "ui_click.wav",
            "click": "ui_click.wav",
            "navigation": "navigation.wav",
            "completion": "completion.wav",
            "error": "soft_error.wav",
            "soft_error": "soft_error.wav",
        }

        filename = sound_map.get(sound_name, "ui_click.wav")
        self._play_file(filename)
        return True

    def stop_all(self) -> None:
        """Immediately stop any playing audio."""
        if HAS_WINSOUND and winsound is not None:
            try:
                winsound.PlaySound(None, 0)
            except Exception:
                pass

    # ========================================================================
    # PREFERENCE MUTATORS & PERSISTENCE
    # ========================================================================

    def set_master_enabled(self, enabled: bool) -> None:
        """Set master audio toggle and persist preference."""
        self.master_enabled = bool(enabled)
        if self.app and hasattr(self.app, "edition_manager"):
            self.app.edition_manager.set_sound_preference(enabled)
        settings = storage.load_settings()
        settings["sound_enabled"] = self.master_enabled
        storage.save_settings(settings)

    def set_volume(self, volume: int) -> None:
        """Set global audio volume (0 to 100) and persist preference."""
        self.volume = max(0, min(100, int(volume)))
        settings = storage.load_settings()
        settings["sound_volume"] = self.volume
        storage.save_settings(settings)

    def set_keypress_enabled(self, enabled: bool) -> None:
        """Set keystroke sound preference and persist."""
        self.sound_keypress = bool(enabled)
        settings = storage.load_settings()
        settings["sound_keypress"] = self.sound_keypress
        storage.save_settings(settings)

    def set_ui_click_enabled(self, enabled: bool) -> None:
        """Set UI interaction sound preference and persist."""
        self.sound_ui_click = bool(enabled)
        settings = storage.load_settings()
        settings["sound_ui_click"] = self.sound_ui_click
        storage.save_settings(settings)

    def set_completion_enabled(self, enabled: bool) -> None:
        """Set completion sound preference and persist."""
        self.sound_completion = bool(enabled)
        settings = storage.load_settings()
        settings["sound_completion"] = self.sound_completion
        storage.save_settings(settings)

    def set_error_enabled(self, enabled: bool) -> None:
        """Set error sound preference and persist."""
        self.sound_error = bool(enabled)
        settings = storage.load_settings()
        settings["sound_error"] = self.sound_error
        storage.save_settings(settings)
