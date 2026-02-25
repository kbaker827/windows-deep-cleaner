#!/usr/bin/env python3
"""
Windows Deep Cleaner - GUI Module

Professional tkinter GUI for the Windows Deep Cleaner.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import platform
import sys
from pathlib import Path

# Handle imports for both regular Python and PyInstaller
# First check if modules were pre-loaded (by main.py)
if 'cleaner' in sys.modules and 'utils' in sys.modules:
    # Modules were pre-loaded, use them
    WindowsCleaner = sys.modules['cleaner'].WindowsCleaner
    format_bytes = sys.modules['utils'].format_bytes
    get_icon = sys.modules['utils'].get_icon
else:
    # Try normal imports
    try:
        from cleaner import WindowsCleaner
        from utils import format_bytes, get_icon
    except ImportError:
        # If running as script, add parent to path
        sys.path.insert(0, str(Path(__file__).parent))
        from cleaner import WindowsCleaner
        from utils import format_bytes, get_icon


class CleanerGUI:
    """Main GUI application"""
    
    def __init__(self, admin=False):
        self.admin = admin
        self.cleaner = WindowsCleaner()
        self.scan_results = {}
        
        self.root = tk.Tk()
        self.root.title("Windows Deep Cleaner")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Set Windows DPI awareness
        if platform.system() == 'Windows':
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_header(main_frame)
        
        # Mode selection
        self._create_mode_section(main_frame)
        
        # Categories
        self._create_categories_section(main_frame)
        
        # Actions
        self._create_actions_section(main_frame)
        
        # Progress
        self._create_progress_section(main_frame)
        
        # Results
        self._create_results_section(main_frame)
        
    def _create_header(self, parent):
        """Create header section"""
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title = ttk.Label(
            header,
            text="🧹 Windows Deep Cleaner",
            font=('Segoe UI', 18, 'bold')
        )
        title.pack(anchor=tk.W)
        
        # Subtitle
        subtitle = ttk.Label(
            header,
            text="Remove unwanted and unnecessary files to free up disk space",
            font=('Segoe UI', 10)
        )
        subtitle.pack(anchor=tk.W)
        
        # Admin status
        if self.admin:
            status_text = "✅ Administrator Mode"
            status_color = 'green'
        else:
            status_text = "ℹ️  Standard User Mode (Machine-wide requires elevation)"
            status_color = 'orange'
            
        status = ttk.Label(
            header,
            text=status_text,
            font=('Segoe UI', 9, 'bold'),
            foreground=status_color
        )
        status.pack(anchor=tk.W, pady=(5, 0))
        
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
    def _create_mode_section(self, parent):
        """Create mode selection section"""
        mode_frame = ttk.LabelFrame(parent, text="Cleaning Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mode_var = tk.StringVar(value='user')
        
        ttk.Radiobutton(
            mode_frame,
            text="👤 Per-User (Current User Only)",
            variable=self.mode_var,
            value='user',
            command=self._on_mode_change
        ).pack(anchor=tk.W)
        
        ttk.Label(
            mode_frame,
            text="    Cleans: Temp files, browser cache, Recycle Bin, user logs",
            font=('Segoe UI', 8),
            foreground='gray'
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            mode_frame,
            text="🖥️  Machine-Wide (All Users - Admin Required)",
            variable=self.mode_var,
            value='system',
            command=self._on_mode_change
        ).pack(anchor=tk.W, pady=(10, 0))
        
        ttk.Label(
            mode_frame,
            text="    Cleans: Windows Update cache, system temp, all user profiles",
            font=('Segoe UI', 8),
            foreground='gray'
        ).pack(anchor=tk.W)
        
        if not self.admin:
            ttk.Label(
                mode_frame,
                text="⚠️  You need to run as Administrator for Machine-Wide mode",
                font=('Segoe UI', 9, 'bold'),
                foreground='red'
            ).pack(anchor=tk.W, pady=(10, 0))
            
    def _create_categories_section(self, parent):
        """Create cleaning categories section"""
        cat_frame = ttk.LabelFrame(parent, text="Categories to Clean", padding="10")
        cat_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create checkboxes for categories
        self.category_vars = {}
        self.category_size_labels = {}
        
        categories = [
            ('temp_files', '📁 Temporary Files', 'Windows and user temp directories'),
            ('browser_cache', '🌐 Browser Cache', 'Chrome, Firefox, Edge cache files'),
            ('windows_update', '🔄 Windows Update Cache', 'Old Windows Update files'),
            ('recycle_bin', '🗑️  Recycle Bin', 'Deleted files in Recycle Bin'),
            ('thumbnails', '🖼️  Thumbnail Cache', 'Windows Explorer thumbnail cache'),
            ('crash_dumps', '💥 Crash Dumps', 'Application crash dump files'),
            ('log_files', '📋 Log Files', 'Application and system logs'),
            ('downloads', '📥 Downloads Folder', 'Old files in Downloads (optional)'),
        ]
        
        for key, label, description in categories:
            frame = ttk.Frame(cat_frame)
            frame.pack(fill=tk.X, pady=2)
            
            var = tk.BooleanVar(value=True)
            self.category_vars[key] = var
            
            cb = ttk.Checkbutton(frame, text=label, variable=var)
            cb.pack(side=tk.LEFT)
            
            ttk.Label(
                frame,
                text=f"- {description}",
                font=('Segoe UI', 8),
                foreground='gray'
            ).pack(side=tk.LEFT, padx=(5, 0))
            
            # Size label (will be updated after scan)
            size_label = ttk.Label(
                frame,
                text="",
                font=('Segoe UI', 8, 'bold'),
                foreground='green'
            )
            size_label.pack(side=tk.RIGHT, padx=(10, 0))
            self.category_size_labels[key] = size_label
            
    def _create_actions_section(self, parent):
        """Create action buttons section"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Scan button
        self.scan_btn = tk.Button(
            action_frame,
            text="🔍 Scan",
            command=self._scan,
            bg='#007bff',
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clean button (disabled until scan)
        self.clean_btn = tk.Button(
            action_frame,
            text="🧹 Clean",
            command=self._clean,
            bg='#28a745',
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.clean_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Dry run checkbox
        self.dry_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            action_frame,
            text="Dry Run (Preview Only)",
            variable=self.dry_run_var
        ).pack(side=tk.LEFT, padx=20)
        
    def _create_progress_section(self, parent):
        """Create progress section"""
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to scan")
        ttk.Label(progress_frame, textvariable=self.status_var).pack(anchor=tk.W)
        
    def _create_results_section(self, parent):
        """Create results section"""
        results_frame = ttk.LabelFrame(parent, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results text
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            height=10
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Summary label
        self.summary_var = tk.StringVar(value="")
        ttk.Label(
            results_frame,
            textvariable=self.summary_var,
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor=tk.W, pady=(10, 0))
        
    def _on_mode_change(self):
        """Handle mode change"""
        mode = self.mode_var.get()
        if mode == 'system' and not self.admin:
            messagebox.showwarning(
                "Admin Required",
                "Machine-Wide mode requires Administrator privileges.\n\n"
                "Please restart the application as Administrator."
            )
            self.mode_var.set('user')
            
    def _log(self, message):
        """Add message to results"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.status_var.set(message[:80])
        
    def _scan(self):
        """Scan for files to clean"""
        self.scan_btn.config(state=tk.DISABLED)
        self.clean_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.results_text.delete(1.0, tk.END)
        
        # Clear previous size labels
        for label in self.category_size_labels.values():
            label.config(text="")
        
        # Get selected categories
        categories = [k for k, v in self.category_vars.items() if v.get()]
        mode = self.mode_var.get()
        
        if not categories:
            messagebox.showwarning("No Categories", "Please select at least one category to scan.")
            self.scan_btn.config(state=tk.NORMAL)
            return
            
        # Run scan in thread
        thread = threading.Thread(target=self._scan_thread, args=(categories, mode))
        thread.start()
        
    def _scan_thread(self, categories, mode):
        """Scan thread"""
        try:
            self._log("🔍 Starting scan...")
            self._log(f"   Mode: {mode}")
            self._log(f"   Categories: {', '.join(categories)}")
            self._log("")
            
            results = self.cleaner.scan(categories, mode, self._update_progress)
            self.scan_results = results
            
            # Display results in a formatted table
            total_size = 0
            total_files = 0
            
            self._log("")
            self._log("="*60)
            self._log("📊 SCAN RESULTS - Space to be freed per category:")
            self._log("="*60)
            self._log("")
            self._log(f"{'Category':<25} {'Size':>15} {'Files':>10}")
            self._log("-"*60)
            
            # Category display names
            category_names = {
                'temp_files': '📁 Temporary Files',
                'browser_cache': '🌐 Browser Cache',
                'windows_update': '🔄 Windows Update',
                'recycle_bin': '🗑️  Recycle Bin',
                'thumbnails': '🖼️  Thumbnails',
                'crash_dumps': '💥 Crash Dumps',
                'log_files': '📋 Log Files',
                'downloads': '📥 Downloads'
            }
            
            for category, data in results.items():
                size = data.get('size', 0)
                files = data.get('files', 0)
                total_size += size
                total_files += files
                
                display_name = category_names.get(category, category)
                self._log(f"{display_name:<25} {format_bytes(size):>15} {files:>10}")
                
                # Update the category size label in the GUI
                if category in self.category_size_labels:
                    if size > 0:
                        self.category_size_labels[category].config(
                            text=f"{format_bytes(size)} ({files} files)"
                        )
                    else:
                        self.category_size_labels[category].config(text="")
                
            self._log("-"*60)
            self._log(f"{'TOTAL':<25} {format_bytes(total_size):>15} {total_files:>10}")
            self._log("="*60)
            self._log("")
            
            self.summary_var.set(f"Scan complete: {format_bytes(total_size)} can be freed")
            self.clean_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            self._log(f"❌ Error during scan: {e}")
            messagebox.showerror("Scan Error", str(e))
        finally:
            self.scan_btn.config(state=tk.NORMAL)
            self.progress_var.set(100)
            
    def _update_progress(self, current, total, message):
        """Update progress bar"""
        if total > 0:
            self.progress_var.set((current / total) * 100)
        self._log(message)
        
    def _clean(self):
        """Clean files"""
        if not self.scan_results:
            messagebox.showwarning("No Scan", "Please scan first before cleaning.")
            return
            
        # Confirm
        dry_run = self.dry_run_var.get()
        mode_text = "DRY RUN (preview only)" if dry_run else "PERMANENTLY DELETE"
        
        if not dry_run:
            result = messagebox.askyesno(
                "Confirm Cleaning",
                f"This will {mode_text} files.\n\n"
                f"Mode: {self.mode_var.get()}\n"
                f"Files will be {'previewed only' if dry_run else 'permanently deleted'}.\n\n"
                "Are you sure?",
                icon='warning'
            )
            if not result:
                return
                
        self.scan_btn.config(state=tk.DISABLED)
        self.clean_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        
        # Run clean in thread
        thread = threading.Thread(target=self._clean_thread, args=(dry_run,))
        thread.start()
        
    def _clean_thread(self, dry_run):
        """Clean thread"""
        try:
            if dry_run:
                self._log("\n🔍 DRY RUN - No files will be deleted\n")
            else:
                self._log("\n🧹 Starting cleaning...\n")
                
            results = self.cleaner.clean(
                self.scan_results,
                dry_run=dry_run,
                progress_callback=self._update_progress
            )
            
            # Display summary
            self._log("\n" + "="*60)
            if dry_run:
                self._log("✅ DRY RUN COMPLETE")
                self._log("   No files were actually deleted")
            else:
                self._log("✅ CLEANING COMPLETE")
                self._log(f"   Space freed: {format_bytes(results.get('total_freed', 0))}")
                self._log(f"   Files deleted: {results.get('files_deleted', 0)}")
            self._log("="*60)
            
            self.summary_var.set("Cleaning complete" if not dry_run else "Dry run complete")
            
            if not dry_run:
                messagebox.showinfo(
                    "Cleaning Complete",
                    f"Successfully freed {format_bytes(results.get('total_freed', 0))}\n"
                    f"Files deleted: {results.get('files_deleted', 0)}"
                )
                
        except Exception as e:
            self._log(f"❌ Error during cleaning: {e}")
            messagebox.showerror("Cleaning Error", str(e))
        finally:
            self.scan_btn.config(state=tk.NORMAL)
            self.clean_btn.config(state=tk.NORMAL)
            self.progress_var.set(100)
            
    def run(self):
        """Run the GUI"""
        self.root.mainloop()


if __name__ == '__main__':
    app = CleanerGUI()
    app.run()
