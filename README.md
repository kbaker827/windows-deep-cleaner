# Windows Deep Cleaner

**A comprehensive Python GUI tool for deep cleaning Windows machines.**

Remove unwanted and unnecessary files to free up disk space. Supports both per-user and machine-wide cleaning modes.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

### Cleaning Categories

- 📁 **Temporary Files** - Windows and user temp directories
- 🌐 **Browser Cache** - Chrome, Firefox, Edge cache files
- 🔄 **Windows Update Cache** - Old Windows Update files
- 🗑️ **Recycle Bin** - Deleted files awaiting permanent removal
- 🖼️ **Thumbnail Cache** - Windows Explorer thumbnail cache
- 💥 **Crash Dumps** - Application crash dump files
- 📋 **Log Files** - Application and system log files
- 📥 **Downloads** - Optional: Old files in Downloads folder

### Modes

- 👤 **Per-User Mode** - Clean current user profile only
- 🖥️ **Machine-Wide Mode** - Clean entire system (requires Admin)

### Safety Features

- ✅ **Scan First** - Preview what will be deleted before cleaning
- ✅ **Dry Run** - Preview mode without actually deleting
- ✅ **Selective Cleaning** - Choose which categories to clean
- ✅ **Size Calculation** - See exactly how much space will be freed
- ✅ **Protected Paths** - Won't delete critical system files
- ✅ **Progress Tracking** - Visual progress bar during cleaning
- ✅ **Detailed Logging** - Full log of all actions

## 📋 Requirements

- Windows 10/11 (7/8 may work but not tested)
- Python 3.7 or higher
- Administrator privileges (for Machine-Wide mode)

## 💻 Installation

### Option 1: Direct Download

```bash
# Clone repository
git clone https://github.com/kbaker827/windows-deep-cleaner.git
cd windows-deep-cleaner

# Run
python main.py
```

### Option 2: Create Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Create standalone executable
pyinstaller --onefile --windowed --name "WindowsDeepCleaner" main.py

# Find executable in dist/ folder
```

## 🎯 Usage

### Quick Start

```bash
# Standard user mode
python main.py

# Run as Administrator for machine-wide cleaning
# (Right-click -> Run as Administrator)
```

### Step-by-Step

1. **Launch the application**
   ```bash
   python main.py
   ```

2. **Select Cleaning Mode**
   - 👤 Per-User: Current user only
   - 🖥️ Machine-Wide: All users (requires Admin)

3. **Choose Categories**
   Check/uncheck categories to clean

4. **Scan**
   Click "🔍 Scan" to see what will be deleted

5. **Review**
   Check the scan results and space to be freed

6. **Clean**
   - Use "Dry Run" first to preview
   - Then click "🧹 Clean" to delete files

## 🖥️ Interface

```
┌─────────────────────────────────────────────────────────────┐
│  🧹 Windows Deep Cleaner                                     │
├─────────────────────────────────────────────────────────────┤
│  ✅ Administrator Mode                                        │
├─────────────────────────────────────────────────────────────┤
│  Cleaning Mode                                               │
│  ○ 👤 Per-User (Current User Only)                          │
│  ● 🖥️ Machine-Wide (All Users - Admin Required)             │
├─────────────────────────────────────────────────────────────┤
│  Categories to Clean                                         │
│  ☑ 📁 Temporary Files - Windows and user temp directories   │
│  ☑ 🌐 Browser Cache - Chrome, Firefox, Edge cache files     │
│  ☑ 🔄 Windows Update Cache - Old Windows Update files       │
│  ☑ 🗑️  Recycle Bin - Deleted files in Recycle Bin            │
│  ...                                                         │
├─────────────────────────────────────────────────────────────┤
│  [🔍 Scan] [🧹 Clean] ☑ Dry Run (Preview Only)              │
├─────────────────────────────────────────────────────────────┤
│  Progress                                                    │
│  [████████████████████░░░░░░░░░░] 67%                       │
│  Scanning browser_cache...                                   │
├─────────────────────────────────────────────────────────────┤
│  Results                                                     │
│  📁 temp_files: 1.2 GB (5234 files)                         │
│  🌐 browser_cache: 856 MB (1234 files)                      │
│  📊 Total: 3.4 GB (8900 files)                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔒 Safety

### Protected Paths

The cleaner will **NEVER** delete:
- Windows System32 files
- Program Files directories
- User profile settings
- System configuration files
- Pagefile, hibernation files

### Recommendations

1. **Always scan first** - See what will be deleted
2. **Use dry run** - Preview without deleting
3. **Start with per-user mode** - Test before system-wide
4. **Close browsers** - Before cleaning browser cache
5. **Keep important downloads** - Don't clean Downloads if unsure

## 🛠️ Command Line Usage

```bash
# Standard GUI
python main.py

# With specific options (future enhancement)
python main.py --mode user --categories temp_files,browser_cache
```

## 📊 Typical Results

| Category | Typical Size | Safety |
|----------|-------------|--------|
| Temp Files | 500 MB - 5 GB | ⭐⭐⭐⭐⭐ |
| Browser Cache | 100 MB - 2 GB | ⭐⭐⭐⭐⭐ |
| Windows Update | 1 GB - 10 GB | ⭐⭐⭐⭐ |
| Recycle Bin | Varies | ⭐⭐⭐⭐⭐ |
| Thumbnails | 50 MB - 500 MB | ⭐⭐⭐⭐⭐ |
| Crash Dumps | 100 MB - 1 GB | ⭐⭐⭐⭐⭐ |
| Log Files | 10 MB - 100 MB | ⭐⭐⭐⭐⭐ |

## 🔧 Troubleshooting

### "Access Denied" Errors

Some files may be in use or require higher privileges:
- Close all browsers before cleaning browser cache
- Run as Administrator for system files
- Some files may be locked by running applications

### Application Won't Start

```bash
# Check Python version
python --version  # Should be 3.7+

# Check tkinter
python -c "import tkinter; print(tkinter.Tcl().eval('info patchlevel'))"
```

### Not Freeing Enough Space

- Check if files are in use by other applications
- Try Machine-Wide mode with Administrator privileges
- Some files may be protected by Windows

## 📝 File Structure

```
windows-deep-cleaner/
├── main.py                 # Entry point
├── scripts/
│   ├── gui.py             # Tkinter GUI (300+ lines)
│   ├── cleaner.py         # Core cleaning logic (350+ lines)
│   └── utils.py           # Utility functions (100+ lines)
├── requirements.txt       # Dependencies (none!)
├── README.md             # This file
└── LICENSE               # MIT License
```

## 🔄 Development

### Running Tests

```bash
# Test utilities
python scripts/utils.py

# Test cleaner (dry run)
python -c "from scripts.cleaner import WindowsCleaner; c = WindowsCleaner(); print(c.scan(['temp_files']))"
```

### Adding New Categories

1. Add checkbox in `gui.py`
2. Add scan method in `cleaner.py`
3. Add icon in `utils.py`

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional cleaning categories
- Registry cleaning (careful!)
- Scheduled cleaning
- More detailed reporting
- Export/import settings

## ⚠️ Disclaimer

**Use at your own risk!**

- Always review what will be deleted
- The authors are not responsible for data loss
- Test on non-critical systems first
- Backup important data before running

## 📄 License

MIT License - See LICENSE file

## 🔗 Links

- **Repository:** https://github.com/kbaker827/windows-deep-cleaner
- **Issues:** https://github.com/kbaker827/windows-deep-cleaner/issues

---

**Free up disk space safely! 🧹💾**

## 📦 Building Executable

### Option 1: Automatic (GitHub Actions)

The executable is automatically built on every release:
1. Go to the [Releases](https://github.com/kbaker827/windows-deep-cleaner/releases) page
2. Download `WindowsDeepCleaner.exe` from the latest release

### Option 2: Build on Windows

If you have Windows with Python installed:

```batch
# Clone the repository
git clone https://github.com/kbaker827/windows-deep-cleaner.git
cd windows-deep-cleaner

# Run the build script
build_exe.bat

# Or manually:
pip install pyinstaller
pyinstaller --onefile --windowed --name "WindowsDeepCleaner" main.py

# Find executable in dist/ folder
```

### Option 3: Build with GitHub Actions

Fork the repository and push a tag to trigger automatic build:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The executable will be available in the Release assets.

## 🚀 Running the Executable

Simply double-click `WindowsDeepCleaner.exe` - no Python installation required!

### For Machine-Wide Cleaning:
1. Right-click on `WindowsDeepCleaner.exe`
2. Select "Run as administrator"
3. Select "🖥️ Machine-Wide" mode

