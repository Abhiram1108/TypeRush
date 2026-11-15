"""
TypeRush Standalone Executable Packaging Tool

Builds a self-contained, single-file Windows executable (dist/TypeRush.exe)
using PyInstaller with assets and icons cleanly bundled.

Usage:
    python build_exe.py
"""

import os
import sys
import shutil
import subprocess

def build():
    print("=" * 70)
    print("TYPERUSH — STANDALONE EXECUTABLE BUILD UTILITY")
    print("=" * 70)

    # 1. Verify PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ Found PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller is not installed.")
        print("To package TypeRush into an executable, install PyInstaller first:")
        print("    pip install pyinstaller")
        print("Then run this script again: python build_exe.py")
        return False

    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(base_dir, "main.py")
    icon_path = os.path.join(base_dir, "assets", "icons", "app.ico")
    
    # 2. Build command arguments
    sep = ";" if sys.platform == "win32" else ":"
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=TypeRush",
        f"--add-data=assets{sep}assets",
        f"--add-data=data{sep}data",
        main_py
    ]

    if os.path.isfile(icon_path):
        cmd.insert(4, f"--icon={icon_path}")
        print(f"✓ Using custom application icon: {icon_path}")

    print("\nExecuting PyInstaller command:")
    print(" ".join(cmd))
    print("\nBuilding... (this may take 30-60 seconds)\n")

    result = subprocess.run(cmd, cwd=base_dir)
    if result.returncode == 0:
        exe_path = os.path.join(base_dir, "dist", "TypeRush.exe" if sys.platform == "win32" else "TypeRush")
        print("\n" + "=" * 70)
        print("✓ BUILD SUCCESSFUL!")
        print(f"Standalone executable created at:\n  {exe_path}")
        print("=" * 70)
        return True
    else:
        print(f"\n✗ Build failed with exit code {result.returncode}")
        return False

if __name__ == "__main__":
    build()
