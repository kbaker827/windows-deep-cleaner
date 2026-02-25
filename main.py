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

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from gui import CleanerGUI


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
