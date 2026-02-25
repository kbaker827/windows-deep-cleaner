#!/usr/bin/env python3
"""
Windows Deep Cleaner - Core Cleaning Module

Handles scanning and cleaning of Windows system files.
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Callable, Optional
import platform


class WindowsCleaner:
    """Main Windows cleaning class"""
    
    def __init__(self):
        self.is_windows = platform.system() == 'Windows'
        self.user_profile = os.environ.get('USERPROFILE', os.path.expanduser('~'))
        self.system_root = os.environ.get('SystemRoot', r'C:\Windows')
        self.program_data = os.environ.get('ProgramData', r'C:\ProgramData')
        
    def scan(self, categories: List[str], mode: str = 'user', 
             progress_callback: Optional[Callable] = None) -> Dict:
        """
        Scan for files to clean
        
        Args:
            categories: List of category keys to scan
            mode: 'user' or 'system'
            progress_callback: Function(current, total, message)
            
        Returns:
            Dict with scan results per category
        """
        results = {}
        total_categories = len(categories)
        
        for i, category in enumerate(categories):
            if progress_callback:
                progress_callback(i, total_categories, f"Scanning {category}...")
                
            if category == 'temp_files':
                results[category] = self._scan_temp_files(mode)
            elif category == 'browser_cache':
                results[category] = self._scan_browser_cache(mode)
            elif category == 'windows_update':
                results[category] = self._scan_windows_update(mode)
            elif category == 'recycle_bin':
                results[category] = self._scan_recycle_bin(mode)
            elif category == 'thumbnails':
                results[category] = self._scan_thumbnails(mode)
            elif category == 'crash_dumps':
                results[category] = self._scan_crash_dumps(mode)
            elif category == 'log_files':
                results[category] = self._scan_log_files(mode)
            elif category == 'downloads':
                results[category] = self._scan_downloads(mode)
                
        if progress_callback:
            progress_callback(total_categories, total_categories, "Scan complete")
            
        return results
        
    def _scan_temp_files(self, mode: str) -> Dict:
        """Scan temporary files"""
        files = []
        total_size = 0
        
        # User temp
        user_temp = os.environ.get('TEMP', os.path.join(self.user_profile, 'AppData', 'Local', 'Temp'))
        temp_files, temp_size = self._scan_directory(user_temp)
        files.extend(temp_files)
        total_size += temp_size
        
        # Windows temp (system mode only)
        if mode == 'system':
            win_temp = os.path.join(self.system_root, 'Temp')
            if os.path.exists(win_temp):
                temp_files, temp_size = self._scan_directory(win_temp)
                files.extend(temp_files)
                total_size += temp_size
                
        # Prefetch (system mode only)
        if mode == 'system':
            prefetch = os.path.join(self.system_root, 'Prefetch')
            if os.path.exists(prefetch):
                temp_files, temp_size = self._scan_directory(prefetch)
                files.extend(temp_files)
                total_size += temp_size
                
        return {'files': len(files), 'size': total_size, 'paths': files}
        
    def _scan_browser_cache(self, mode: str) -> Dict:
        """Scan browser cache files"""
        files = []
        total_size = 0
        
        # Chrome
        chrome_cache = os.path.join(self.user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Cache')
        if os.path.exists(chrome_cache):
            temp_files, temp_size = self._scan_directory(chrome_cache)
            files.extend(temp_files)
            total_size += temp_size
            
        # Chrome Code Cache
        chrome_code_cache = os.path.join(self.user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Code Cache')
        if os.path.exists(chrome_code_cache):
            temp_files, temp_size = self._scan_directory(chrome_code_cache)
            files.extend(temp_files)
            total_size += temp_size
            
        # Edge
        edge_cache = os.path.join(self.user_profile, 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache')
        if os.path.exists(edge_cache):
            temp_files, temp_size = self._scan_directory(edge_cache)
            files.extend(temp_files)
            total_size += temp_size
            
        # Firefox
        firefox_profile = os.path.join(self.user_profile, 'AppData', 'Local', 'Mozilla', 'Firefox', 'Profiles')
        if os.path.exists(firefox_profile):
            for profile in os.listdir(firefox_profile):
                cache_path = os.path.join(firefox_profile, profile, 'cache2')
                if os.path.exists(cache_path):
                    temp_files, temp_size = self._scan_directory(cache_path)
                    files.extend(temp_files)
                    total_size += temp_size
                    
        return {'files': len(files), 'size': total_size, 'paths': files}
        
    def _scan_windows_update(self, mode: str) -> Dict:
        """Scan Windows Update cache"""
        files = []
        total_size = 0
        
        if mode != 'system':
            return {'files': 0, 'size': 0, 'paths': []}
            
        # SoftwareDistribution\Download
        wu_cache = os.path.join(self.system_root, 'SoftwareDistribution', 'Download')
        if os.path.exists(wu_cache):
            temp_files, temp_size = self._scan_directory(wu_cache)
            files.extend(temp_files)
            total_size += temp_size
            
        return {'files': len(files), 'size': total_size, 'paths': files}
        
    def _scan_recycle_bin(self, mode: str) -> Dict:
        """Scan Recycle Bin"""
        files = []
        total_size = 0
        
        # User Recycle Bin
        recycle_bin = os.path.join(self.user_profile, '$Recycle.Bin')
        if os.path.exists(recycle_bin):
            temp_files, temp_size = self._scan_directory(recycle_bin)
            files.extend(temp_files)
            total_size += temp_size
            
        return {'files': len(files), 'size': total_size, 'paths': files}
        
    def _scan_thumbnails(self, mode: str) -> Dict:
        """Scan thumbnail cache"""
        files = []
        total_size = 0
        
        thumb_cache = os.path.join(self.user_profile, 'AppData', 'Local', 'Microsoft', 'Windows', 'Explorer')
        if os.path.exists(thumb_cache):
            for f in os.listdir(thumb_cache):
                if f.startswith('thumbcache_'):
                    filepath = os.path.join(thumb_cache, f)
                    if os.path.isfile(filepath):
                        files.append(filepath)
                        total_size += os.path.getsize(filepath)
                        
        return {'files': len(files), 'size': total_size, 'paths': files}
        
    def _scan_crash_dumps(self, mode: str) -> Dict:
        """Scan crash dump files"""
        files = []
        total_size = 0
        
        # LocalDumps
        dumps_path = os.path.join(self.user_profile, 'AppData', 'Local', 'CrashDumps')
        if os.path.exists(dumps_path):
            temp_files, temp_size = self._scan_directory(dumps_path)
            files.extend(temp_files)
            total_size += temp_size
            
        # Windows crash dumps (system)
        if mode == 'system':
            win_dumps = os.path.join(self.system_root, 'Minidump')
            if os.path.exists(win_dumps):
                temp_files, temp_size = self._scan_directory(win_dumps)
                files.extend(temp_files)
                total_size += temp_size
                
        return {'files': len(files), 'size': total_size, 'paths': files}
        
    def _scan_log_files(self, mode: str) -> Dict:
        """Scan log files"""
        files = []
        total_size = 0
        
        # User logs
        log_paths = [
            os.path.join(self.user_profile, 'AppData', 'Local', 'Microsoft', 'Windows', 'Explorer'),
            os.path.join(self.user_profile, 'AppData', 'Local', 'Temp'),
        ]
        
        for log_path in log_paths:
            if os.path.exists(log_path):
                for root, dirs, filenames in os.walk(log_path):
                    for filename in filenames:
                        if filename.endswith('.log'):
                            filepath = os.path.join(root, filename)
                            files.append(filepath)
                            total_size += os.path.getsize(filepath)
                            
        return {'files': len(files), 'size': total_size, 'paths': files}
        
    def _scan_downloads(self, mode: str) -> Dict:
        """Scan Downloads folder (optional)"""
        files = []
        total_size = 0
        
        downloads = os.path.join(self.user_profile, 'Downloads')
        if os.path.exists(downloads):
            temp_files, temp_size = self._scan_directory(downloads)
            files.extend(temp_files)
            total_size += temp_size
            
        return {'files': len(files), 'size': total_size, 'paths': files}
        
    def _scan_directory(self, path: str) -> tuple:
        """Scan directory for files, return (file_list, total_size)"""
        files = []
        total_size = 0
        
        if not os.path.exists(path):
            return files, total_size
            
        try:
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    try:
                        filepath = os.path.join(root, filename)
                        if os.path.isfile(filepath):
                            files.append(filepath)
                            total_size += os.path.getsize(filepath)
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass
            
        return files, total_size
        
    def clean(self, scan_results: Dict, dry_run: bool = False,
              progress_callback: Optional[Callable] = None) -> Dict:
        """
        Clean files based on scan results
        
        Args:
            scan_results: Results from scan()
            dry_run: If True, only preview what would be deleted
            progress_callback: Function(current, total, message)
            
        Returns:
            Dict with cleaning results
        """
        total_freed = 0
        files_deleted = 0
        
        # Count total files
        total_files = sum(data.get('files', 0) for data in scan_results.values())
        current = 0
        
        for category, data in scan_results.items():
            paths = data.get('paths', [])
            
            for filepath in paths:
                current += 1
                
                if progress_callback:
                    progress_callback(current, total_files, f"Processing: {filepath[:60]}...")
                    
                if os.path.exists(filepath):
                    try:
                        size = os.path.getsize(filepath)
                        
                        if not dry_run:
                            if os.path.isfile(filepath):
                                os.remove(filepath)
                            elif os.path.isdir(filepath):
                                shutil.rmtree(filepath)
                                
                        total_freed += size
                        files_deleted += 1
                        
                    except (OSError, PermissionError) as e:
                        if progress_callback:
                            progress_callback(current, total_files, f"⚠️  Could not delete: {filepath} - {e}")
                            
        if progress_callback:
            progress_callback(total_files, total_files, "Cleaning complete")
            
        return {
            'total_freed': total_freed,
            'files_deleted': files_deleted,
            'dry_run': dry_run
        }
