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

# Determine base path (works for both Python and PyInstaller)
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    BASE_DIR = Path(sys.executable).parent
else:
    # Running in normal Python
    BASE_DIR = Path(__file__).parent

SCRIPTS_DIR = BASE_DIR / 'scripts'

# Debug info (will show in console)
print(f"Base directory: {BASE_DIR}")
print(f"Scripts directory: {SCRIPTS_DIR}")
print(f"Scripts exists: {SCRIPTS_DIR.exists()}")
if SCRIPTS_DIR.exists():
    print(f"Scripts contents: {list(SCRIPTS_DIR.glob('*.py'))}")

# Function to load module from file
def load_module_from_file(module_name, file_path):
    """Load a Python module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load all required modules
try:
    # Load utils first (needed by cleaner and gui)
    utils_path = SCRIPTS_DIR / 'utils.py'
    if not utils_path.exists():
        raise FileNotFoundError(f"utils.py not found at {utils_path}")
    utils_module = load_module_from_file('utils', utils_path)
    format_bytes = utils_module.format_bytes
    
    # Load cleaner
    cleaner_path = SCRIPTS_DIR / 'cleaner.py'
    if not cleaner_path.exists():
        raise FileNotFoundError(f"cleaner.py not found at {cleaner_path}")
    cleaner_module = load_module_from_file('cleaner', cleaner_path)
    WindowsCleaner = cleaner_module.WindowsCleaner
    
    # Load gui
    gui_path = SCRIPTS_DIR / 'gui.py'
    if not gui_path.exists():
        raise FileNotFoundError(f"gui.py not found at {gui_path}")
    
    # Before loading gui, we need to inject the other modules into sys.modules
    # so gui.py can find them
    sys.modules['utils'] = utils_module
    sys.modules['cleaner'] = cleaner_module
    
    gui_module = load_module_from_file('gui', gui_path)
    CleanerGUI = gui_module.CleanerGUI
    
    print("✅ All modules loaded successfully")
    
except Exception as e:
    print(f"❌ Error loading modules: {e}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"sys.path: {sys.path}")
    
    # Show error dialog if possible
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Import Error",
            f"Failed to load required modules:\n\n{str(e)}\n\n"
            f"Base directory: {BASE_DIR}\n"
            f"Scripts directory: {SCRIPTS_DIR}\n"
            f"Scripts exists: {SCRIPTS_DIR.exists()}"
        )
        root.destroy()
    except:
        pass
    
    sys.exit(1)


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
    try:
        app = CleanerGUI(admin=admin)
        app.run()
    except Exception as e:
        print(f"❌ Error running GUI: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Runtime Error", f"Error running application:\n\n{str(e)}")
            root.destroy()
        except:
            pass
        
        sys.exit(1)


if __name__ == '__main__':
    main()
