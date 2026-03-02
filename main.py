#!/usr/bin/env python3
"""
Windows Deep Cleaner - Main Entry Point

A comprehensive Windows system cleaning tool with GUI.
Supports per-user and machine-wide cleaning modes.
"""

import sys
import os
import ctypes
from pathlib import Path
import importlib.util


def get_base_dir() -> Path:
    """Get the base directory, handling PyInstaller bundling."""
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        return Path(sys.executable).parent
    return Path(__file__).parent


def find_scripts_dir() -> Path:
    """Find the scripts directory."""
    base_dir = get_base_dir()
    candidates = [
        base_dir / 'scripts',
        base_dir / 'windows-deep-cleaner' / 'scripts',
        Path(base_dir).parent / 'scripts',
        base_dir,
    ]
    if hasattr(sys, '_MEIPASS'):
        meipass = Path(sys._MEIPASS)
        candidates += [meipass / 'scripts', meipass / 'windows-deep-cleaner' / 'scripts']

    for path in candidates:
        if path.exists() and (path / 'gui.py').exists():
            return path

    return base_dir / 'scripts'


BASE_DIR = get_base_dir()
SCRIPTS_DIR = find_scripts_dir()


def _load_module(name: str, path: Path):
    """Load a Python module from a file path and register it in sys.modules."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _find_script(filename: str) -> Path:
    """Locate a script file relative to SCRIPTS_DIR / BASE_DIR."""
    for candidate in (SCRIPTS_DIR / filename, BASE_DIR / filename):
        if candidate.exists():
            return candidate
    for match in BASE_DIR.rglob(filename):
        return match
    return None


def _load_all_modules():
    """Load utils, cleaner, and gui modules; raise on failure."""
    utils_path = _find_script('utils.py')
    if not utils_path:
        raise FileNotFoundError(f"utils.py not found (searched: {SCRIPTS_DIR}, {BASE_DIR})")

    cleaner_path = _find_script('cleaner.py')
    if not cleaner_path:
        raise FileNotFoundError(f"cleaner.py not found (searched: {SCRIPTS_DIR}, {BASE_DIR})")

    gui_path = _find_script('gui.py')
    if not gui_path:
        raise FileNotFoundError(f"gui.py not found (searched: {SCRIPTS_DIR}, {BASE_DIR})")

    utils_mod = _load_module('utils', utils_path)
    cleaner_mod = _load_module('cleaner', cleaner_path)
    # gui.py resolves its own imports via sys.modules, so register first
    sys.modules['utils'] = utils_mod
    sys.modules['cleaner'] = cleaner_mod
    gui_mod = _load_module('gui', gui_path)
    return gui_mod.CleanerGUI


def _show_error_dialog(title: str, message: str):
    """Display a tkinter error dialog (best-effort)."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        pass


def is_admin() -> bool:
    """Return True if the process has administrator privileges."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def main():
    if sys.platform != 'win32':
        _show_error_dialog("Unsupported Platform", "Windows Deep Cleaner requires Windows.")
        sys.exit(1)

    try:
        CleanerGUI = _load_all_modules()
    except Exception as exc:
        _show_error_dialog(
            "Import Error",
            f"Failed to load required modules:\n\n{exc}\n\n"
            f"Base directory: {BASE_DIR}\n"
            f"Scripts directory: {SCRIPTS_DIR}",
        )
        sys.exit(1)

    try:
        app = CleanerGUI(admin=is_admin())
        app.run()
    except Exception as exc:
        import traceback
        _show_error_dialog("Runtime Error", f"Error running application:\n\n{exc}\n\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == '__main__':
    main()
