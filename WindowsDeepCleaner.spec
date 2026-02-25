# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the base directory
base_dir = Path(SPECDIR)

block_cipher = None

# Add all scripts as data files
scripts_dir = base_dir / 'scripts'
scripts_data = [(str(scripts_dir), 'scripts')]

a = Analysis(
    ['main.py'],
    pathex=[str(base_dir)],
    binaries=[],
    datas=scripts_data,
    hiddenimports=[
        'platform',
        'ctypes',
        'pathlib',
        'importlib.util',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'threading',
        'os',
        'sys',
        'shutil',
        'tempfile',
        'typing',
        'datetime',
        'json',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WindowsDeepCleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed mode
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
