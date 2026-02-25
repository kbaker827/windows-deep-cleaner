#!/usr/bin/env python3
"""
Windows Deep Cleaner - Utility Functions
"""

import os


def format_bytes(size_bytes: int) -> str:
    """
    Format bytes to human readable string
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    if size_bytes == 0:
        return "0 B"
        
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
        
    return f"{size:.2f} {units[unit_index]}"


def get_icon(category: str) -> str:
    """Get emoji icon for category"""
    icons = {
        'temp_files': '📁',
        'browser_cache': '🌐',
        'windows_update': '🔄',
        'recycle_bin': '🗑️',
        'thumbnails': '🖼️',
        'crash_dumps': '💥',
        'log_files': '📋',
        'downloads': '📥',
    }
    return icons.get(category, '📄')


def is_safe_to_delete(filepath: str) -> bool:
    """
    Check if a file is safe to delete
    
    Args:
        filepath: Path to file
        
    Returns:
        True if safe to delete
    """
    # List of protected paths/patterns
    protected = [
        'Windows\\System32',
        'Windows\\SysWOW64',
        'Program Files',
        'Program Files (x86)',
        'Users\\Default',
        'Users\\Public',
        'pagefile.sys',
        'hiberfil.sys',
        'swapfile.sys',
    ]
    
    filepath_lower = filepath.lower()
    
    for pattern in protected:
        if pattern.lower() in filepath_lower:
            return False
            
    return True


def get_windows_version() -> str:
    """Get Windows version string"""
    import platform
    import sys
    
    if sys.platform != 'win32':
        return "Not Windows"
        
    try:
        version = platform.win32_ver()
        return f"Windows {version[0]} {version[1]}"
    except:
        return "Windows (version unknown)"


def check_disk_space(path: str = 'C:\\') -> dict:
    """
    Check disk space
    
    Args:
        path: Drive path
        
    Returns:
        Dict with total, used, free space
    """
    try:
        import shutil
        total, used, free = shutil.disk_usage(path)
        return {
            'total': total,
            'used': used,
            'free': free,
            'percent_used': (used / total) * 100 if total > 0 else 0
        }
    except Exception as e:
        return {'error': str(e)}


class Logger:
    """Simple logger for the cleaner"""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file
        self.messages = []
        
    def log(self, message: str, level: str = 'INFO'):
        """Log a message"""
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        self.messages.append(log_entry)
        
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
                
    def info(self, message: str):
        self.log(message, 'INFO')
        
    def warning(self, message: str):
        self.log(message, 'WARNING')
        
    def error(self, message: str):
        self.log(message, 'ERROR')
        
    def get_logs(self) -> list:
        """Get all log messages"""
        return self.messages


if __name__ == '__main__':
    # Test utilities
    print("Testing format_bytes:")
    print(f"  1024 = {format_bytes(1024)}")
    print(f"  1048576 = {format_bytes(1048576)}")
    print(f"  1073741824 = {format_bytes(1073741824)}")
    
    print("\nTesting get_windows_version:")
    print(f"  {get_windows_version()}")
    
    print("\nTesting check_disk_space:")
    space = check_disk_space()
    if 'error' not in space:
        print(f"  Total: {format_bytes(space['total'])}")
        print(f"  Used: {format_bytes(space['used'])}")
        print(f"  Free: {format_bytes(space['free'])}")
        print(f"  Used %: {space['percent_used']:.1f}%")
