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

# Handle both regular Python and PyInstaller bundled execution
def get_script_dir():
    """Get the scripts directory, handling PyInstaller bundling"""
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = Path(sys.executable).parent
    else:
        # Running in normal Python
        base_path = Path(__file__).parent
    
    # Add scripts directory to path
    scripts_dir = base_path / 'scripts'
    if scripts_dir.exists():
        sys.path.insert(0, str(scripts_dir))
    
    return base_path

# Set up paths
BASE_DIR = get_script_dir()

# Try importing with fallback
try:
    from gui import CleanerGUI
except ImportError:
    # If scripts is in path but import fails, try direct import
    try:
        import importlib.util
        gui_path = BASE_DIR / 'scripts' / 'gui.py'
        if gui_path.exists():
            spec = importlib.util.spec_from_file_location("gui", gui_path)
            gui_module = importlib.util.module_from_spec(spec)
            sys.modules['gui'] = gui_module
            spec.loader.exec_module(gui_module)
            CleanerGUI = gui_module.CleanerGUI
        else:
            raise FileNotFoundError(f"gui.py not found at {gui_path}")
    except Exception as e:
        print(f"Error loading GUI module: {e}")
        print(f"Python path: {sys.path}")
        print(f"Base directory: {BASE_DIR}")
        print(f"Scripts directory exists: {(BASE_DIR / 'scripts').exists()}")
        raise


def is_admin():
    """Check if running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def main():
    """Main entry point"""
    # Check if on Windows
    if sys.platform != 'win32':
        print("⚠️  This tool is designed for Windows.")
        print("   Some features may not work on other platforms.")
    
    # Check admin status
    admin = is_admin()
    if admin:
        print("✅ Running with administrator privileges")
    else:
        print("ℹ️  Running without administrator privileges")
        print("   Machine-wide cleaning will require elevation")
    
    # Launch GUI
    app = CleanerGUI(admin=admin)
    app.run()


if __name__ == '__main__':
    main()
