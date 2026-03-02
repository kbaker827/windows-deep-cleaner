#!/usr/bin/env python3
"""
Windows Deep Cleaner - Core Cleaning Module

Handles scanning and cleaning of Windows system files.
"""

import os
import sys
import shutil
import ctypes
from pathlib import Path
from typing import Dict, List, Callable, Optional, Tuple
import platform


def _get_user_sid() -> str:
    """Return the SID string for the current user, or empty string on failure."""
    try:
        import subprocess
        result = subprocess.run(
            ['whoami', '/user', '/fo', 'csv', '/nh'],
            capture_output=True, text=True, timeout=5
        )
        # Output: "DOMAIN\user","S-1-5-..."
        parts = result.stdout.strip().strip('"').split('","')
        if len(parts) == 2:
            return parts[1].strip('"')
    except Exception:
        pass
    return ''


class WindowsCleaner:
    """Core Windows system cleaning class."""

    def __init__(self):
        self.is_windows = platform.system() == 'Windows'
        self.user_profile = os.environ.get('USERPROFILE', os.path.expanduser('~'))
        self.local_app_data = os.environ.get('LOCALAPPDATA',
                                              os.path.join(self.user_profile, 'AppData', 'Local'))
        self.roaming_app_data = os.environ.get('APPDATA',
                                               os.path.join(self.user_profile, 'AppData', 'Roaming'))
        self.system_root = os.environ.get('SystemRoot', r'C:\Windows')
        self.program_data = os.environ.get('ProgramData', r'C:\ProgramData')

        self._scan_dispatch: Dict[str, Callable] = {
            'temp_files':     self._scan_temp_files,
            'browser_cache':  self._scan_browser_cache,
            'windows_update': self._scan_windows_update,
            'recycle_bin':    self._scan_recycle_bin,
            'thumbnails':     self._scan_thumbnails,
            'crash_dumps':    self._scan_crash_dumps,
            'log_files':      self._scan_log_files,
            'downloads':      self._scan_downloads,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan(self, categories: List[str], mode: str = 'user',
             progress_callback: Optional[Callable] = None) -> Dict:
        """
        Scan for files to clean.

        Args:
            categories: List of category keys to scan.
            mode: 'user' or 'system'.
            progress_callback: Callable(current, total, message).

        Returns:
            Dict mapping category key -> {'files': int, 'size': int, 'paths': list}.
        """
        results = {}
        total = len(categories)

        for i, category in enumerate(categories):
            if progress_callback:
                progress_callback(i, total, f"Scanning {category}...")
            scanner = self._scan_dispatch.get(category)
            if scanner:
                results[category] = scanner(mode)
            else:
                results[category] = {'files': 0, 'size': 0, 'paths': []}

        if progress_callback:
            progress_callback(total, total, "Scan complete")

        return results

    def clean(self, scan_results: Dict, dry_run: bool = False,
              progress_callback: Optional[Callable] = None) -> Dict:
        """
        Delete (or preview) all files from scan_results.

        Args:
            scan_results: Output of scan().
            dry_run: If True, no files are actually deleted.
            progress_callback: Callable(current, total, message).

        Returns:
            {'total_freed': int, 'files_deleted': int, 'errors': int, 'dry_run': bool}
        """
        total_freed = 0
        files_deleted = 0
        errors = 0

        all_paths = [
            (path, category)
            for category, data in scan_results.items()
            for path in data.get('paths', [])
        ]
        total_files = len(all_paths)

        for current, (filepath, category) in enumerate(all_paths, 1):
            if progress_callback and current % 50 == 0:
                progress_callback(current, total_files, f"Processing {current}/{total_files}...")

            if not os.path.exists(filepath):
                continue

            try:
                size = os.path.getsize(filepath)
                if not dry_run:
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                    elif os.path.isdir(filepath):
                        shutil.rmtree(filepath, ignore_errors=True)
                total_freed += size
                files_deleted += 1
            except (OSError, PermissionError):
                errors += 1

        if progress_callback:
            progress_callback(total_files, total_files, "Cleaning complete")

        return {
            'total_freed': total_freed,
            'files_deleted': files_deleted,
            'errors': errors,
            'dry_run': dry_run,
        }

    # ------------------------------------------------------------------
    # Scan helpers
    # ------------------------------------------------------------------

    def _scan_temp_files(self, mode: str) -> Dict:
        files, size = [], 0

        # User %TEMP%
        user_temp = os.environ.get('TEMP',
                                   os.path.join(self.local_app_data, 'Temp'))
        f, s = self._scan_directory(user_temp)
        files += f; size += s

        if mode == 'system':
            for path in (
                os.path.join(self.system_root, 'Temp'),
                os.path.join(self.system_root, 'Prefetch'),
            ):
                f, s = self._scan_directory(path)
                files += f; size += s

        return {'files': len(files), 'size': size, 'paths': files}

    def _scan_browser_cache(self, mode: str) -> Dict:
        files, size = [], 0

        # Chrome-based browsers (Chrome, Edge, Brave, Opera, Vivaldi)
        chrome_bases = {
            'Chrome':  os.path.join(self.local_app_data, 'Google', 'Chrome', 'User Data'),
            'Edge':    os.path.join(self.local_app_data, 'Microsoft', 'Edge', 'User Data'),
            'Brave':   os.path.join(self.local_app_data, 'BraveSoftware', 'Brave-Browser', 'User Data'),
            'Opera':   os.path.join(self.roaming_app_data, 'Opera Software', 'Opera Stable'),
            'Vivaldi': os.path.join(self.local_app_data, 'Vivaldi', 'User Data'),
        }

        cache_subdirs = ['Cache', 'Code Cache', 'GPUCache', 'Network', 'Service Worker',
                         'Storage', 'Application Cache']

        for browser, base in chrome_bases.items():
            if not os.path.exists(base):
                continue
            # Enumerate profiles: Default + Profile N
            profiles = ['Default']
            try:
                profiles += [
                    d for d in os.listdir(base)
                    if d.startswith('Profile ') and os.path.isdir(os.path.join(base, d))
                ]
            except OSError:
                pass

            for profile in profiles:
                for subdir in cache_subdirs:
                    path = os.path.join(base, profile, subdir)
                    f, s = self._scan_directory(path)
                    files += f; size += s

        # Firefox / Waterfox / Thunderbird
        for app_dir in (
            os.path.join(self.local_app_data, 'Mozilla', 'Firefox', 'Profiles'),
            os.path.join(self.roaming_app_data, 'Mozilla', 'Firefox', 'Profiles'),
            os.path.join(self.roaming_app_data, 'Waterfox', 'Profiles'),
            os.path.join(self.roaming_app_data, 'Thunderbird', 'Profiles'),
        ):
            if not os.path.exists(app_dir):
                continue
            try:
                for profile in os.listdir(app_dir):
                    for subdir in ('cache2', 'startupCache', 'thumbnails'):
                        f, s = self._scan_directory(os.path.join(app_dir, profile, subdir))
                        files += f; size += s
            except OSError:
                pass

        # Legacy Internet Explorer / Edge HTML cache
        ie_cache = os.path.join(self.local_app_data, 'Microsoft', 'Windows', 'INetCache')
        f, s = self._scan_directory(ie_cache)
        files += f; size += s

        return {'files': len(files), 'size': size, 'paths': files}

    def _scan_windows_update(self, mode: str) -> Dict:
        if mode != 'system':
            return {'files': 0, 'size': 0, 'paths': []}

        files, size = [], 0
        for path in (
            os.path.join(self.system_root, 'SoftwareDistribution', 'Download'),
            os.path.join(self.system_root, 'SoftwareDistribution', 'DeliveryOptimization'),
        ):
            f, s = self._scan_directory(path)
            files += f; size += s

        return {'files': len(files), 'size': size, 'paths': files}

    def _scan_recycle_bin(self, mode: str) -> Dict:
        """
        Enumerate $Recycle.Bin using the current user's SID.
        Falls back to scanning all drives' $Recycle.Bin folders in system mode.
        """
        files, size = [], 0

        sid = _get_user_sid()

        # Collect drive letters (C: is always tried; add mounted volumes too)
        drives = set()
        for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
            drive = f'{letter}:\\'
            if os.path.exists(drive):
                drives.add(drive)

        for drive in sorted(drives):
            bin_root = os.path.join(drive, '$Recycle.Bin')
            if not os.path.exists(bin_root):
                continue

            if sid:
                # Only the current user's bin
                user_bin = os.path.join(bin_root, sid)
                f, s = self._scan_directory(user_bin)
                files += f; size += s
            elif mode == 'system':
                # No SID available; scan all user buckets
                try:
                    for entry in os.listdir(bin_root):
                        f, s = self._scan_directory(os.path.join(bin_root, entry))
                        files += f; size += s
                except OSError:
                    pass

        return {'files': len(files), 'size': size, 'paths': files}

    def _scan_thumbnails(self, mode: str) -> Dict:
        files, size = [], 0

        explorer_dir = os.path.join(
            self.local_app_data, 'Microsoft', 'Windows', 'Explorer'
        )
        if os.path.exists(explorer_dir):
            try:
                for name in os.listdir(explorer_dir):
                    if name.startswith('thumbcache_'):
                        path = os.path.join(explorer_dir, name)
                        if os.path.isfile(path):
                            files.append(path)
                            try:
                                size += os.path.getsize(path)
                            except OSError:
                                pass
            except OSError:
                pass

        return {'files': len(files), 'size': size, 'paths': files}

    def _scan_crash_dumps(self, mode: str) -> Dict:
        files, size = [], 0

        # User crash dumps
        for path in (
            os.path.join(self.local_app_data, 'CrashDumps'),
            os.path.join(self.local_app_data, 'Microsoft', 'Windows', 'WER', 'ReportArchive'),
            os.path.join(self.local_app_data, 'Microsoft', 'Windows', 'WER', 'ReportQueue'),
        ):
            f, s = self._scan_directory(path)
            files += f; size += s

        if mode == 'system':
            for path in (
                os.path.join(self.system_root, 'Minidump'),
                os.path.join(self.program_data, 'Microsoft', 'Windows', 'WER', 'ReportArchive'),
                os.path.join(self.program_data, 'Microsoft', 'Windows', 'WER', 'ReportQueue'),
            ):
                f, s = self._scan_directory(path)
                files += f; size += s

        return {'files': len(files), 'size': size, 'paths': files}

    def _scan_log_files(self, mode: str) -> Dict:
        files, size = [], 0

        user_log_roots = [
            os.path.join(self.local_app_data, 'Temp'),
            os.path.join(self.local_app_data, 'Microsoft', 'Windows'),
        ]

        for log_root in user_log_roots:
            if not os.path.exists(log_root):
                continue
            try:
                for root, _dirs, filenames in os.walk(log_root):
                    for name in filenames:
                        if name.lower().endswith(('.log', '.log.bak')):
                            path = os.path.join(root, name)
                            files.append(path)
                            try:
                                size += os.path.getsize(path)
                            except OSError:
                                pass
            except (OSError, PermissionError):
                pass

        if mode == 'system':
            win_logs = os.path.join(self.system_root, 'Logs')
            try:
                for root, _dirs, filenames in os.walk(win_logs):
                    for name in filenames:
                        if name.lower().endswith('.log'):
                            path = os.path.join(root, name)
                            files.append(path)
                            try:
                                size += os.path.getsize(path)
                            except OSError:
                                pass
            except (OSError, PermissionError):
                pass

        return {'files': len(files), 'size': size, 'paths': files}

    def _scan_downloads(self, mode: str) -> Dict:
        """Scan Downloads folder for incomplete/temporary download artifacts only."""
        files, size = [], 0

        # File extensions that are safe to remove (incomplete/temp downloads)
        temp_extensions = {
            '.crdownload',  # Chrome partial download
            '.part',        # Firefox partial download
            '.tmp',
            '.download',    # Safari partial
            '.partial',
            '.opdownload',  # Opera partial
        }

        downloads = os.path.join(self.user_profile, 'Downloads')
        if not os.path.exists(downloads):
            return {'files': 0, 'size': 0, 'paths': []}

        try:
            for name in os.listdir(downloads):
                path = os.path.join(downloads, name)
                if os.path.isfile(path):
                    ext = os.path.splitext(name)[1].lower()
                    if ext in temp_extensions:
                        files.append(path)
                        try:
                            size += os.path.getsize(path)
                        except OSError:
                            pass
        except OSError:
            pass

        return {'files': len(files), 'size': size, 'paths': files}

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    def _scan_directory(self, path: str) -> Tuple[List[str], int]:
        """Recursively collect files under path. Returns (file_list, total_size)."""
        files: List[str] = []
        total_size = 0

        if not path or not os.path.exists(path):
            return files, total_size

        try:
            for root, _dirs, filenames in os.walk(path):
                for name in filenames:
                    filepath = os.path.join(root, name)
                    try:
                        if os.path.isfile(filepath):
                            files.append(filepath)
                            total_size += os.path.getsize(filepath)
                    except OSError:
                        continue
        except (OSError, PermissionError):
            pass

        return files, total_size
