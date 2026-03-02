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
if 'cleaner' in sys.modules and 'utils' in sys.modules:
    WindowsCleaner = sys.modules['cleaner'].WindowsCleaner
    format_bytes = sys.modules['utils'].format_bytes
    get_icon = sys.modules['utils'].get_icon
    check_disk_space = sys.modules['utils'].check_disk_space
else:
    try:
        from cleaner import WindowsCleaner
        from utils import format_bytes, get_icon, check_disk_space
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent))
        from cleaner import WindowsCleaner
        from utils import format_bytes, get_icon, check_disk_space


CATEGORY_NAMES = {
    'temp_files':     '📁 Temporary Files',
    'browser_cache':  '🌐 Browser Cache',
    'windows_update': '🔄 Windows Update',
    'recycle_bin':    '🗑️  Recycle Bin',
    'thumbnails':     '🖼️  Thumbnails',
    'crash_dumps':    '💥 Crash Dumps',
    'log_files':      '📋 Log Files',
    'downloads':      '📥 Downloads (temp)',
}


class CleanerGUI:
    """Main GUI application."""

    def __init__(self, admin: bool = False):
        self.admin = admin
        self.cleaner = WindowsCleaner()
        self.scan_results: dict = {}
        self._cancel_flag = threading.Event()

        self.root = tk.Tk()
        self.root.title("Windows Deep Cleaner")
        self.root.geometry("1020x860")
        self.root.minsize(900, 750)

        if platform.system() == 'Windows':
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        self._build_header(main)
        self._build_mode_section(main)
        self._build_categories_section(main)
        self._build_actions_section(main)
        self._build_progress_section(main)
        self._build_results_section(main)

    def _build_header(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(frame, text="🧹 Windows Deep Cleaner",
                  font=('Segoe UI', 16, 'bold')).pack(anchor=tk.W)
        ttk.Label(frame, text="Remove unwanted and unnecessary files to free up disk space",
                  font=('Segoe UI', 9)).pack(anchor=tk.W)

        status_text = "✅ Administrator Mode" if self.admin else "ℹ️  Standard User Mode"
        status_color = 'green' if self.admin else 'orange'
        ttk.Label(frame, text=status_text, font=('Segoe UI', 8, 'bold'),
                  foreground=status_color).pack(anchor=tk.W)

        # Disk space display
        self._disk_var = tk.StringVar(value=self._get_disk_summary())
        ttk.Label(frame, textvariable=self._disk_var,
                  font=('Segoe UI', 8), foreground='#555').pack(anchor=tk.W)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

    def _build_mode_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Cleaning Mode", padding=5)
        frame.pack(fill=tk.X, pady=(0, 5))

        self.mode_var = tk.StringVar(value='user')
        ttk.Radiobutton(frame, text="👤 Per-User (Current User)",
                        variable=self.mode_var, value='user',
                        command=self._on_mode_change).pack(anchor=tk.W)
        ttk.Radiobutton(frame, text="🖥️  Machine-Wide (All Users - Admin Required)",
                        variable=self.mode_var, value='system',
                        command=self._on_mode_change).pack(anchor=tk.W)

    def _build_categories_section(self, parent):
        outer = ttk.LabelFrame(parent, text="Categories to Clean", padding=5)
        outer.pack(fill=tk.X, pady=(0, 5))

        # Select All / None buttons
        btn_row = ttk.Frame(outer)
        btn_row.pack(fill=tk.X, pady=(0, 3))
        ttk.Button(btn_row, text="Select All",
                   command=self._select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row, text="Select None",
                   command=self._select_none).pack(side=tk.LEFT)

        left = ttk.Frame(outer)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right = ttk.Frame(outer)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.category_vars: dict[str, tk.BooleanVar] = {}
        self.category_size_labels: dict[str, ttk.Label] = {}

        left_cats = [
            ('temp_files',     '📁 Temporary Files'),
            ('browser_cache',  '🌐 Browser Cache'),
            ('windows_update', '🔄 Windows Update'),
            ('recycle_bin',    '🗑️  Recycle Bin'),
        ]
        right_cats = [
            ('thumbnails',  '🖼️  Thumbnails'),
            ('crash_dumps', '💥 Crash Dumps'),
            ('log_files',   '📋 Log Files'),
            ('downloads',   '📥 Downloads (temp)'),
        ]

        def add_row(col_frame, key, label):
            row = ttk.Frame(col_frame)
            row.pack(fill=tk.X, pady=1)
            var = tk.BooleanVar(value=True)
            self.category_vars[key] = var
            ttk.Checkbutton(row, text=label, variable=var).pack(side=tk.LEFT)
            size_lbl = ttk.Label(row, text="", font=('Segoe UI', 8, 'bold'),
                                 foreground='green')
            size_lbl.pack(side=tk.RIGHT, padx=(5, 0))
            self.category_size_labels[key] = size_lbl

        for key, label in left_cats:
            add_row(left, key, label)
        for key, label in right_cats:
            add_row(right, key, label)

    def _build_actions_section(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 5))

        self.scan_btn = tk.Button(
            frame, text="🔍 Scan", command=self._scan,
            bg='#007bff', fg='white', font=('Segoe UI', 10, 'bold'),
            padx=15, pady=5, cursor='hand2')
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.clean_btn = tk.Button(
            frame, text="🧹 Clean", command=self._clean,
            bg='#28a745', fg='white', font=('Segoe UI', 10, 'bold'),
            padx=15, pady=5, cursor='hand2', state=tk.DISABLED)
        self.clean_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.cancel_btn = tk.Button(
            frame, text="✖ Cancel", command=self._cancel,
            bg='#dc3545', fg='white', font=('Segoe UI', 10, 'bold'),
            padx=15, pady=5, cursor='hand2', state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.dry_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Dry Run (preview only)",
                        variable=self.dry_run_var).pack(side=tk.LEFT)

    def _build_progress_section(self, parent):
        frame = ttk.LabelFrame(parent, text="Progress", padding=5)
        frame.pack(fill=tk.X, pady=(0, 5))

        self.progress_var = tk.DoubleVar(value=0)
        ttk.Progressbar(frame, variable=self.progress_var,
                        maximum=100, mode='determinate').pack(fill=tk.X)

        self.status_var = tk.StringVar(value="Ready to scan")
        ttk.Label(frame, textvariable=self.status_var,
                  font=('Segoe UI', 8)).pack(anchor=tk.W)

    def _build_results_section(self, parent):
        frame = ttk.LabelFrame(parent, text="📊 Results", padding=5)
        frame.pack(fill=tk.BOTH, expand=True)

        self.summary_var = tk.StringVar(
            value="👉 Click '🔍 Scan' to see what can be cleaned")
        ttk.Label(frame, textvariable=self.summary_var,
                  font=('Segoe UI', 10, 'bold'),
                  foreground='#007bff').pack(anchor=tk.W, pady=(0, 5))

        self.results_text = scrolledtext.ScrolledText(
            frame, wrap=tk.WORD, font=('Consolas', 9),
            height=10, bg='#f5f5f5')
        self.results_text.pack(fill=tk.BOTH, expand=True)

        self.results_text.insert(tk.END,
            "Welcome! Select categories above and click Scan.\n"
            "💡 Tip: Use 'Dry Run' first to preview deletions.\n")
        self.results_text.config(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_mode_change(self):
        if self.mode_var.get() == 'system' and not self.admin:
            messagebox.showwarning(
                "Admin Required",
                "Machine-Wide mode requires Administrator privileges.\n\n"
                "Please restart the application as Administrator.")
            self.mode_var.set('user')

    def _select_all(self):
        for var in self.category_vars.values():
            var.set(True)

    def _select_none(self):
        for var in self.category_vars.values():
            var.set(False)

    def _cancel(self):
        self._cancel_flag.set()
        self._set_status("Cancelling...")

    # ------------------------------------------------------------------
    # Thread-safe GUI update helpers
    # ------------------------------------------------------------------

    def _after(self, fn, *args):
        """Schedule fn(*args) on the main thread."""
        self.root.after(0, fn, *args)

    def _append_log(self, message: str):
        """Append a line to the log (must be called on main thread)."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)

    def _set_status(self, message: str):
        """Update status label (safe to call from any thread via _after)."""
        self.status_var.set(message[:100])

    def _set_progress(self, value: float):
        self.progress_var.set(value)

    def _log(self, message: str):
        """Thread-safe log append."""
        self._after(self._append_log, message)

    def _update_progress(self, current: int, total: int, message: str):
        """Progress callback – safe from background threads."""
        pct = (current / total * 100) if total > 0 else 0
        self._after(self._set_progress, pct)
        self._after(self._set_status, message)

    # ------------------------------------------------------------------
    # Scan
    # ------------------------------------------------------------------

    def _scan(self):
        categories = [k for k, v in self.category_vars.items() if v.get()]
        if not categories:
            messagebox.showwarning("No Categories",
                                   "Please select at least one category to scan.")
            return

        self._cancel_flag.clear()
        self._set_buttons(scanning=True)
        self._set_progress(0)
        self._clear_size_labels()

        # Clear log
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)

        threading.Thread(
            target=self._scan_worker,
            args=(categories, self.mode_var.get()),
            daemon=True).start()

    def _scan_worker(self, categories: list, mode: str):
        try:
            self._log("🔍 Starting scan...")
            self._log(f"   Mode: {mode}")
            self._log(f"   Categories: {', '.join(categories)}")
            self._log("")

            results = self.cleaner.scan(categories, mode, self._update_progress)
            self.scan_results = results

            total_size = sum(d.get('size', 0) for d in results.values())
            total_files = sum(d.get('files', 0) for d in results.values())

            self._log("=" * 60)
            self._log("📊 SCAN RESULTS")
            self._log("=" * 60)
            self._log(f"{'Category':<28} {'Size':>12} {'Files':>8}")
            self._log("-" * 60)

            for cat, data in results.items():
                s = data.get('size', 0)
                f = data.get('files', 0)
                name = CATEGORY_NAMES.get(cat, cat)
                self._log(f"{name:<28} {format_bytes(s):>12} {f:>8,}")

                # Update size label on main thread
                if cat in self.category_size_labels:
                    label_text = f"{format_bytes(s)} ({f:,})" if s > 0 else ""
                    self._after(
                        self.category_size_labels[cat].config,
                        text=label_text)

            self._log("-" * 60)
            self._log(f"{'TOTAL':<28} {format_bytes(total_size):>12} {total_files:>8,}")
            self._log("=" * 60)

            summary = f"Scan complete: {format_bytes(total_size)} can be freed ({total_files:,} files)"
            self._after(self.summary_var.set, summary)
            self._after(self.clean_btn.config, state=tk.NORMAL)

        except Exception as exc:
            self._log(f"❌ Error during scan: {exc}")
            self._after(messagebox.showerror, "Scan Error", str(exc))
        finally:
            self._after(self._set_buttons, False)
            self._after(self._set_progress, 100)

    # ------------------------------------------------------------------
    # Clean
    # ------------------------------------------------------------------

    def _clean(self):
        if not self.scan_results:
            messagebox.showwarning("No Scan", "Please scan first before cleaning.")
            return

        dry_run = self.dry_run_var.get()
        if not dry_run:
            if not messagebox.askyesno(
                "Confirm Cleaning",
                f"This will PERMANENTLY DELETE the scanned files.\n\n"
                f"Mode: {self.mode_var.get()}\n\n"
                "Are you sure?",
                icon='warning'):
                return

        self._cancel_flag.clear()
        self._set_buttons(scanning=True)
        self._set_progress(0)

        threading.Thread(
            target=self._clean_worker,
            args=(dry_run,),
            daemon=True).start()

    def _clean_worker(self, dry_run: bool):
        try:
            prefix = "🔍 DRY RUN" if dry_run else "🧹 Cleaning"
            self._log(f"\n{prefix} – starting...\n")

            results = self.cleaner.clean(
                self.scan_results,
                dry_run=dry_run,
                progress_callback=self._update_progress)

            freed = results.get('total_freed', 0)
            deleted = results.get('files_deleted', 0)
            errors = results.get('errors', 0)

            self._log("\n" + "=" * 60)
            if dry_run:
                self._log("✅ DRY RUN COMPLETE — no files were deleted")
                self._log(f"   Would free: {format_bytes(freed)} ({deleted:,} files)")
            else:
                self._log("✅ CLEANING COMPLETE")
                self._log(f"   Space freed: {format_bytes(freed)}")
                self._log(f"   Files deleted: {deleted:,}")
                if errors:
                    self._log(f"   Skipped (locked/permission): {errors:,}")
            self._log("=" * 60)

            summary = ("Dry run complete" if dry_run
                       else f"Done – freed {format_bytes(freed)} ({deleted:,} files)")
            self._after(self.summary_var.set, summary)

            # Refresh disk space display
            self._after(self._disk_var.set, self._get_disk_summary())

            if not dry_run:
                self._after(
                    messagebox.showinfo,
                    "Cleaning Complete",
                    f"Freed {format_bytes(freed)}\nFiles deleted: {deleted:,}"
                    + (f"\nSkipped: {errors:,}" if errors else ""))

        except Exception as exc:
            self._log(f"❌ Error during cleaning: {exc}")
            self._after(messagebox.showerror, "Cleaning Error", str(exc))
        finally:
            self._after(self._set_buttons, False)
            self._after(self._set_progress, 100)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_buttons(self, scanning: bool):
        """Enable/disable buttons for active vs idle state."""
        idle_state = tk.DISABLED if scanning else tk.NORMAL
        active_state = tk.NORMAL if scanning else tk.DISABLED
        self.scan_btn.config(state=idle_state)
        self.clean_btn.config(
            state=tk.DISABLED if scanning else
            (tk.NORMAL if self.scan_results else tk.DISABLED))
        self.cancel_btn.config(state=active_state)

    def _clear_size_labels(self):
        for lbl in self.category_size_labels.values():
            lbl.config(text="")

    def _get_disk_summary(self) -> str:
        try:
            space = check_disk_space('C:\\')
            if 'error' not in space:
                from utils import format_bytes as _fb
                return (f"C: drive — {_fb(space['free'])} free of "
                        f"{_fb(space['total'])} ({space['percent_used']:.1f}% used)")
        except Exception:
            pass
        return ""

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    app = CleanerGUI()
    app.run()
