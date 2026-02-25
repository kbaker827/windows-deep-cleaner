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
def get_base_dir():
    """Get the base directory, handling PyInstaller bundling"""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        # PyInstaller puts files in a temp folder (_MEIPASS) or next to exe
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        else:
            return Path(sys.executable).parent
    else:
        # Running in normal Python
        return Path(__file__).parent

def find_scripts_dir():
    """Find the scripts directory in various possible locations"""
    base_dir = get_base_dir()
    
    # Possible locations for scripts
    possible_paths = [
        base_dir / 'scripts',                           # scripts/ next to exe
        base_dir / 'windows-deep-cleaner' / 'scripts',  # In subfolder
        Path(base_dir).parent / 'scripts',              # Parent directory
        base_dir,                                        # Scripts in same dir
    ]
    
    # If PyInstaller, also check _MEIPASS subdirectories
    if hasattr(sys, '_MEIPASS'):
        meipass = Path(sys._MEIPASS)
        possible_paths.extend([
            meipass / 'scripts',
            meipass / 'windows-deep-cleaner' / 'scripts',
        ])
    
    # Check each path
    for path in possible_paths:
        if path.exists():
            # Check if required files exist
            if (path / 'gui.py').exists():
                return path
    
    # If not found, return the most likely one for error reporting
    return base_dir / 'scripts'

# Get directories
BASE_DIR = get_base_dir()
SCRIPTS_DIR = find_scripts_dir()

# Debug info (will show in console)
print(f"Python executable: {sys.executable}")
print(f"Frozen: {getattr(sys, 'frozen', False)}")
print(f"_MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}")
print(f"Base directory: {BASE_DIR}")
print(f"Base dir contents: {list(BASE_DIR.iterdir()) if BASE_DIR.exists() else 'N/A'}")
print(f"Scripts directory: {SCRIPTS_DIR}")
print(f"Scripts exists: {SCRIPTS_DIR.exists()}")

# If scripts doesn't exist, list what's in base to debug
if not SCRIPTS_DIR.exists():
    print(f"\nContents of base directory ({BASE_DIR}):")
    try:
        for item in BASE_DIR.iterdir():
            print(f"  {item.name} {'(dir)' if item.is_dir() else ''}")
            if item.is_dir():
                try:
                    for subitem in item.iterdir():
                        print(f"    {subitem.name}")
                except:
                    pass
    except Exception as e:
        print(f"  Error listing: {e}")
else:
    print(f"Scripts contents: {list(SCRIPTS_DIR.glob('*.py'))}")

# Function to load module from file
def load_module_from_file(module_name, file_path):
    """Load a Python module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Try to find scripts in different locations
def find_script_file(filename):
    """Find a script file in various locations"""
    # Direct path
    direct_path = SCRIPTS_DIR / filename
    if direct_path.exists():
        return direct_path
    
    # In base directory
    base_path = BASE_DIR / filename
    if base_path.exists():
        return base_path
    
    # Search recursively in base
    for py_file in BASE_DIR.rglob(filename):
        return py_file
    
    return None

# Load all required modules
try:
    # Load utils first (needed by cleaner and gui)
    utils_path = find_script_file('utils.py')
    if not utils_path:
        raise FileNotFoundError(f"utils.py not found. Searched in: {SCRIPTS_DIR}, {BASE_DIR}")
    print(f"Loading utils from: {utils_path}")
    utils_module = load_module_from_file('utils', utils_path)
    format_bytes = utils_module.format_bytes
    
    # Load cleaner
    cleaner_path = find_script_file('cleaner.py')
    if not cleaner_path:
        raise FileNotFoundError(f"cleaner.py not found. Searched in: {SCRIPTS_DIR}, {BASE_DIR}")
    print(f"Loading cleaner from: {cleaner_path}")
    cleaner_module = load_module_from_file('cleaner', cleaner_path)
    WindowsCleaner = cleaner_module.WindowsCleaner
    
    # Load gui
    gui_path = find_script_file('gui.py')
    if not gui_path:
        raise FileNotFoundError(f"gui.py not found. Searched in: {SCRIPTS_DIR}, {BASE_DIR}")
    print(f"Loading gui from: {gui_path}")
    
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
